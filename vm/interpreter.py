import os
import threading
from concurrent.futures import ThreadPoolExecutor
import re
import random
from . ast_nodes import *
from . parser import FuncCall
from . token_type import TokenType
from colorama import Fore, Back, Style
from . environment import Environment, NOT_FOUND
from . lambda_function import LambdaFunction
from . return_Value import ReturnValue
from . user_function import UserFunction
from . runtime_instance import RuntimeInstance, RuntimeInstance_for_enum
from . runtime_class import RuntimeClass
from . runtime_enum import RuntimeEnum
from . native_constructeur import NativeCollectionsConstruct as constuct
from . native_funcs import NativeFuncs as Funcs
from . native_funcs import _ia_ollama_stream
from . native_collections import NativeCollectionsFuncs as ColFuncs
from . native_advanced_funcs import NativeAdvancedFuncs as AdvFuncs
from . lexer import tokenize
from . parser import Parser
from . module_proxy import ModuleProxy
from . neuron_db import NeuronLoopDB, NeuroRuntime, RefEntryRuntime, RefMarker, CategoryStore, CapacityFullError


#from . heart.heart import Heart
#DEBUG = False  # mettre True pour traces détaillées
class Interpreter:
    # --- self.env / self.current_instance / self.current_return_type sont
    # désormais PAR THREAD (via threading.local) plutôt que des attributs
    # d'instance partagés. Chaque thread a sa propre "pile" d'environnements
    # d'exécution — c'est ce qui permet à Scheduler.runConcurrent() de faire
    # tourner du VRAI code Oktopios en parallèle sur plusieurs threads sans
    # qu'ils se piétinent (avant : un seul verrou global sérialisait tout).
    # Les structures réellement PARTAGÉES (self.tentacles, self.matches_db,
    # self.hearts, self.classes...) restent des attributs normaux et doivent
    # toujours passer par self._shared_lock pour toute mutation concurrente.
    @property
    def env(self):
        return getattr(self._thread_local, "env", self.global_env)

    @env.setter
    def env(self, value):
        self._thread_local.env = value

    @property
    def current_instance(self):
        return getattr(self._thread_local, "current_instance", None)

    @current_instance.setter
    def current_instance(self, value):
        self._thread_local.current_instance = value

    @property
    def current_return_type(self):
        return getattr(self._thread_local, "current_return_type", None)

    @current_return_type.setter
    def current_return_type(self, value):
        self._thread_local.current_return_type = value

    def __init__(self):
        self._thread_local = threading.local()
        self.global_env = Environment()
        self.env = self.global_env
        self.current_return_type = None
        self.current_instance = None  # ← ici on déclare current_instance
        self.in_expr_context = False
        self.native_construct = {**constuct}
        self.native_funcs = { **AdvFuncs, **Funcs, **ColFuncs}

        # --- Namespaces natifs liés à CETTE instance d'interpréteur (Heart "ExecutionFlow") ---
        self.native_funcs["Tentacle"] = {
            "create": lambda template_name, *args: self.create_tentacle(template_name, list(args)),
            "count": lambda: len(self.tentacles),
            "list": lambda: OktopiosList([t.klass.name for t in self.tentacles]),
        }
        self.native_funcs["Scheduler"] = {
            "schedule": lambda intention_name, *args: self.schedule_task(intention_name, list(args)),
            "run": lambda: self.run_scheduler(sequential=True),
            "runConcurrent": lambda: self.run_scheduler(sequential=False),
            "pending": lambda: len(self.task_queue),
        }
        self.native_funcs["Heart"] = {
            "call": lambda heart_name, func_name, *args: self.call_heart_function(heart_name, func_name, list(args)),
            "get": lambda heart_name, var_name: self.get_heart_var(heart_name, var_name),
            "list": lambda: OktopiosList(list(self.hearts.keys())),
        }
        self.native_funcs["Core"] = {
            "call": lambda func_name, *args: self.call_core_function(func_name, list(args)),
            "get": lambda var_name: self.get_core_var(var_name),
            "set": lambda var_name, value: self.set_core_var(var_name, value),
        }
        self.native_funcs["Monitor"] = {
            "snapshot": lambda: self.monitor_snapshot(),
            "tentacles": lambda: OktopiosList([
                OktopiosMap({"classe": t.klass.name, "champs": list(t.fields.keys())})
                for t in self.tentacles
            ]),
            "log": lambda *args: self.monitor_log(args),
            "history": lambda: OktopiosList(list(self.monitor_events)),
        }
        self.native_funcs["MatchesDB"] = {
            "save": lambda db_name, path: self.save_matches_db(db_name, path),
            "load": lambda db_name, path: self.load_matches_db(db_name, path),
        }
        # Étendre IAModule avec le fallback en cascade + le streaming (ont
        # besoin de l'interpréteur : rappeler un backend différent, ou
        # invoquer une fonction Oktopios à chaque morceau de texte reçu).
        self.native_funcs["IAModule"]["callWithFallback"] = lambda prompt, backends: self.ia_call_with_fallback(prompt, backends)
        self.native_funcs["IAModule"]["ollamaStream"] = lambda prompt, on_chunk, model="llama3", host="http://localhost:11434", timeout=60: self.ia_ollama_stream(prompt, on_chunk, model, host, timeout)
        self.native_funcs["Director"] = {
            "call": lambda func_name, *args: self.call_director_function(func_name, list(args)),
        }
        self.native_funcs["Supervisor"] = {
            "call": lambda name, func_name, *args: self.call_supervisor_function(name, func_name, list(args)),
            "list": lambda: OktopiosList(list(self.supervisors.keys())),
        }
        self.native_funcs["Agent"] = {
            "call": lambda name, func_name, *args: self.call_agent_function(name, func_name, list(args)),
            "list": lambda: OktopiosList(list(self.agent_blocks.keys())),
        }
        self.native_funcs["Secretary"] = {
            "call": lambda func_name, *args: self.call_secretary_function(func_name, list(args)),
        }
        self.native_funcs["MultiAgent"] = {
            "run": lambda tache: self.run_multi_agent(tache),
        }
        self.native_funcs["AdaptiveEngine"] = {
            "run": lambda situation, options, backend="ollama", model=None, api_key=None: self.adaptive_run(situation, options, backend, model, api_key),
            "recall": lambda situation, threshold=1: self.adaptive_recall(situation, threshold),
            "memory": lambda: self.adaptive_memory_list(),
        }
        self.variables = {}
        self.checkargMeth = {}
        self.fieldsMeth = {}
        self.classes = {}  # ← TABLE DES CLASSES
        self.interfaces = {}
        self.abstract_classes = {}
        self.enums = {}
        self.central_tent = None
        self.tentacles = []
        self.tentacle_templates = {}  # nom de classe 'ten' -> class_decl (pour createTentacle())
        self.hearts = {}              # nom du coeur -> HeartBlock (Heart1/2/3...)
        self.core_env = None          # noyau partagé (core{}) : parent de tous les hearts
        self.director_env = None      # director{} : singleton, coordonne les superviseurs
        self.supervisors = {}         # nom -> {"block":..., "env":...}
        self.agent_blocks = {}        # nom -> {"block":..., "env":...} (distinct de self.tentacles/ten class)
        self.secretary_env = None     # secretary{} : singleton, interface de réponse
        self.adaptive_memory_db = None  # mémoire d'expérience de l'AdaptiveEngine (neuron_loop dédié)
        self.monitor_events = []      # historique pour Monitor.log/history (Heart 3 : "IA & Monitoring")
        self.task_queue = []          # file de tâches pour le scheduler (Heart "ExecutionFlow")
        self._shared_lock = threading.RLock()  # protège UNIQUEMENT les structures partagées (tentacules, matches_db, scheduler, hearts/core, monitor) ; le reste du code Oktopios tourne en vrai parallèle grâce aux self.env thread-local ci-dessus
        self.heart_config = {}
        self.modules_loaded =  []
        self.modules_loaded_alias =  {}
        self.module_cache = {}  # module_name -> namespace dict
        self.module_search_paths = [
            os.getcwd(),  # current working dir
            os.path.join(os.getcwd(), "modules"),  # ./modules
            # tu peux ajouter d'autres dossiers relatifs au projet
        ]
        self.matches_db = {}  # nom de la base -> NeuronLoopDB (déclarations neuron_loop)
        #self.env.define("heart", Heart())

    # ---- INTERPRÉTATION ----
    def interpret(self, program: Program):
        candidate_classes = []

        # Étape 1 : enregistrer toutes les fonctions dans l'environnement
        self.Visite_Function_declar(program)

        # ------------------------
        # 1️⃣ Enregistrer toutes les interfaces
        # ------------------------
        for stmt in program.body:
            if isinstance(stmt, InterfaceDeclaration):
                self.interfaces[stmt.name] = stmt
                #print(f"[Interface enregistrée] {stmt.name}")

        # ------------------------
        # 2️⃣ Enregistrer toutes les classes (abstraites et concrètes)
        # ------------------------
        for stmt in program.body:
            class_stmt = stmt.class_decl if isinstance(stmt, (TentClass, TenClass)) else stmt
            if isinstance(class_stmt, ClassDeclaration):
                if getattr(class_stmt, "is_abstract", False):
                    with self._shared_lock:
                        self.abstract_classes[class_stmt.name] = class_stmt
                    #print(f"[Classe Abstraite] {class_stmt.name}")
                else:
                    with self._shared_lock:
                        self.classes[class_stmt.name] = class_stmt
                    #print(f"[Classe Concrete] {class_stmt.name}")

        # ------------------------
        # 3️⃣ Résoudre héritage et interfaces
        # ------------------------
        self.resolve_inheritance_and_validate()
        self.validate_interface_contracts()

        # ------------------------
        # 4️⃣ Détecter classes avec main()
        # ------------------------
        for stmt in self.classes.values():
            #print(stmt.members)
            if any(isinstance(m, FunDecl) and m.name == "main" for m in getattr(stmt, "methods", [])):
                candidate_classes.append(stmt)

        # ------------------------
        # 5️⃣ Exécuter code top-level (hors classes/fonctions)
        # ------------------------
        for stmt in program.body:
            if not isinstance(stmt, (FunDecl, ClassDeclaration, InterfaceDeclaration)):
                #print(f"Debug : dans intepreter : {stmt}")
                self.execute(stmt)

        # ------------------------
        # 6️⃣ Instancier et activer les classes avec main()
        # ------------------------
        for target_class in candidate_classes:
            if getattr(target_class, "is_abstract", False):
                #print(f"[Erreur] Impossible d’instancier la classe abstraite {target_class.name}")
                continue
            instance = RuntimeInstance(target_class)
            method = instance.get_method_bound("main")
            if method:
                #print(f"[Auto] Activation implicite de {target_class.name}.main()")
                method.call(self, [])

    def visit_TentClass(self, stmt):
        self.central_tent = stmt
        with self._shared_lock:
            self.classes[stmt.name] = stmt.class_decl
        # CORE en premier : c'est le "noyau" partagé que tous les hearts
        # peuvent ensuite lire (contrairement aux hearts, isolés entre eux).
        for member in stmt.body:
            if isinstance(member, CoreBlock):
                self.visit_CoreBlock(member)
        for member in stmt.body:
            if isinstance(member, HeartBlock):
                self.visit_HeartBlock(member)
        # Architecture multi-agents (MASTER_SPECIFICATION.md) : director en
        # premier (coordinateur), puis supervisors/agents (indépendants entre
        # eux), puis secretary (interface terminale).
        for member in stmt.body:
            if isinstance(member, DirectorBlock):
                self.visit_DirectorBlock(member)
        for member in stmt.body:
            if isinstance(member, SupervisorBlock):
                self.visit_SupervisorBlock(member)
        for member in stmt.body:
            if isinstance(member, AgentBlock):
                self.visit_AgentBlock(member)
        for member in stmt.body:
            if isinstance(member, SecretaryBlock):
                self.visit_SecretaryBlock(member)
        return None

    def visit_TenClass(self, stmt):
        with self._shared_lock:
            self.classes[stmt.name] = stmt.class_decl
            self.tentacle_templates[stmt.name] = stmt.class_decl
        instance = self.instantiate_class(stmt.class_decl, args=[])
        with self._shared_lock:
            self.tentacles.append(instance)
        return None

    def create_tentacle(self, template_name, args=None):
        """'Create Tentacle()' du schéma : instancie dynamiquement une nouvelle
        tentacule à partir d'un template 'ten class' déjà déclaré, et l'ajoute
        au pool de tentacules dispatchable par intention/tentRandom."""
        class_decl = self.tentacle_templates.get(template_name)
        if class_decl is None:
            raise Exception(
                f"[Erreur] Aucun template de tentacule 'ten class {template_name}' trouvé "
                f"(templates disponibles : {list(self.tentacle_templates.keys())})"
            )
        instance = self.instantiate_class(class_decl, args=args or [])
        with self._shared_lock:
            self.tentacles.append(instance)
        return instance

    def schedule_task(self, intention_name, args):
        """Heart 'ExecutionFlow' : place une intention en attente au lieu de
        la diffuser immédiatement à toutes les tentacules — la planification
        devient un acte explicite plutôt qu'un effet de bord."""
        with self._shared_lock:
            self.task_queue.append((intention_name, args))
            return len(self.task_queue)

    def run_scheduler(self, sequential=True):
        """Exécute les tâches en attente.

        - sequential=True  (Scheduler.run) : une tâche après l'autre, ordre
          déterministe — équivalent à plusieurs 'intention' à la suite.
        - sequential=False (Scheduler.runConcurrent) : dispatché sur un VRAI
          pool de threads. Grâce à self.env (et current_instance/
          current_return_type) en stockage PAR THREAD, deux tentacules
          peuvent maintenant exécuter du code Oktopios EN MEME TEMPS sans se
          piétiner — ce n'est plus juste une concurrence "d'attente réseau".
          Seules les structures réellement PARTAGÉES (tentacules, bases
          __matches_db__, scheduler, hearts/core, monitoring) restent
          protégées par un verrou fin (self._shared_lock), localisé à chaque
          point de mutation plutôt qu'autour de toute l'exécution.
        """
        with self._shared_lock:
            tasks = self.task_queue
            self.task_queue = []

        def run_one(intention_name, args):
            for tentacle in list(self.tentacles):
                self.dispatch_to_tentacle(tentacle, intention_name, args, required=False)
            return intention_name

        results = []
        if sequential or len(tasks) <= 1:
            for name, args in tasks:
                results.append(run_one(name, args))
        else:
            with ThreadPoolExecutor(max_workers=min(8, len(tasks))) as pool:
                futures = [pool.submit(run_one, name, args) for name, args in tasks]
                for f in futures:
                    results.append(f.result())

        return OktopiosList(results)

    def visit_HeartBlock(self, stmt):
        # Chaque heart{} a son PROPRE environnement, isolé des autres hearts,
        # mais dont le PARENT est le noyau partagé (core{}) s'il existe : un
        # heart peut donc LIRE l'état central, sans jamais polluer le scope
        # global ni les autres hearts.
        heart_env = Environment(enclosing=self.core_env or self.env)
        prev_env = self.env
        self.env = heart_env
        try:
            for s in stmt.body:
                self.execute(s)
        finally:
            self.env = prev_env

        if getattr(stmt, "name", None):
            with self._shared_lock:
                self.hearts[stmt.name] = {"block": stmt, "env": heart_env}
        return None

    def call_heart_function(self, heart_name, func_name, args=None):
        """Heart.call('ExecutionFlow', 'status', ...) : invoque une fonction
        définie DANS le scope isolé d'un cœur nommé."""
        heart = self.hearts.get(heart_name)
        if heart is None:
            raise Exception(
                f"[Erreur] Aucun heart nommé '{heart_name}' trouvé "
                f"(cœurs disponibles : {list(self.hearts.keys())})"
            )
        args = args or []
        func = heart["env"].get(func_name, suppress_errors=True)
        if func is NOT_FOUND:
            func = heart["env"].get(f"{func_name}/{len(args)}", suppress_errors=True)
        if func is NOT_FOUND or not isinstance(func, UserFunction):
            raise Exception(
                f"[Erreur] Aucune fonction '{func_name}' dans le heart '{heart_name}'"
            )
        return func.call(self, args)

    def get_heart_var(self, heart_name, var_name):
        """Heart.get('DataCirculation', 'cache') : lit une variable définie
        dans le scope isolé d'un cœur nommé."""
        heart = self.hearts.get(heart_name)
        if heart is None:
            raise Exception(f"[Erreur] Aucun heart nommé '{heart_name}' trouvé")
        value = heart["env"].get(var_name, suppress_errors=True)
        return None if value is NOT_FOUND else value

    def visit_CoreBlock(self, stmt):
        # Le "noyau" est UNIQUE et PARTAGÉ : plusieurs core{} dans le même
        # tent class s'accumulent dans le MÊME environnement (contrairement
        # aux hearts, isolés chacun de leur côté). C'est l'état central que
        # tous les hearts peuvent ensuite lire.
        with self._shared_lock:
            if self.core_env is None:
                self.core_env = Environment(enclosing=self.env)
        prev_env = self.env
        self.env = self.core_env
        try:
            for s in stmt.body:
                self.execute(s)
        finally:
            self.env = prev_env
        return None

    def call_core_function(self, func_name, args=None):
        """Core.call('configurer', ...) : invoque une fonction définie dans
        le noyau partagé."""
        if self.core_env is None:
            raise Exception("[Erreur] Aucun 'core{}' déclaré dans ce programme")
        args = args or []
        func = self.core_env.get(func_name, suppress_errors=True)
        if func is NOT_FOUND:
            func = self.core_env.get(f"{func_name}/{len(args)}", suppress_errors=True)
        if func is NOT_FOUND or not isinstance(func, UserFunction):
            raise Exception(f"[Erreur] Aucune fonction '{func_name}' dans le core")
        return func.call(self, args)

    def get_core_var(self, var_name):
        if self.core_env is None:
            raise Exception("[Erreur] Aucun 'core{}' déclaré dans ce programme")
        value = self.core_env.get(var_name, suppress_errors=True)
        return None if value is NOT_FOUND else value

    def set_core_var(self, var_name, value):
        with self._shared_lock:
            if self.core_env is None:
                self.core_env = Environment(enclosing=self.env)
            self.core_env.define(var_name, value=value)
        return value

    # ------------------------------------------------------------------
    # Architecture multi-agents : director / supervisor / agent / secretary
    # (MASTER_SPECIFICATION.md — Priorité n°1)
    # ------------------------------------------------------------------
    def _run_isolated_block(self, stmt, parent_env=None):
        """Exécute le corps d'un bloc pieuvre dans un environnement isolé et
        renvoie cet environnement (mécanisme commun à heart/core/director/
        supervisor/agent/secretary)."""
        block_env = Environment(enclosing=parent_env or self.env)
        prev_env = self.env
        self.env = block_env
        try:
            for s in stmt.body:
                self.execute(s)
        finally:
            self.env = prev_env
        return block_env

    def visit_DirectorBlock(self, stmt):
        # Singleton (comme core{}) : coordonne les superviseurs.
        env = self._run_isolated_block(stmt)
        with self._shared_lock:
            self.director_env = env
        return None

    def visit_SupervisorBlock(self, stmt):
        env = self._run_isolated_block(stmt)
        name = getattr(stmt, "name", None) or f"supervisor_{len(self.supervisors) + 1}"
        with self._shared_lock:
            self.supervisors[name] = {"block": stmt, "env": env}
        return None

    def visit_AgentBlock(self, stmt):
        env = self._run_isolated_block(stmt)
        name = getattr(stmt, "name", None) or f"agent_{len(self.agent_blocks) + 1}"
        with self._shared_lock:
            self.agent_blocks[name] = {"block": stmt, "env": env}
        return None

    def visit_SecretaryBlock(self, stmt):
        # Singleton : sert d'interface, reçoit les demandes, renvoie les réponses.
        env = self._run_isolated_block(stmt)
        with self._shared_lock:
            self.secretary_env = env
        return None

    def _call_in_env(self, env, func_name, args):
        """Appelle func_name(args...) dans `env` s'il existe, sinon renvoie
        None (les rôles sans cette fonction sont de simples passe-plat)."""
        if env is None:
            return None
        func = env.get(func_name, suppress_errors=True)
        if func is NOT_FOUND:
            func = env.get(f"{func_name}/{len(args)}", suppress_errors=True)
        if func is NOT_FOUND or not isinstance(func, UserFunction):
            return None
        return func.call(self, args)

    def call_director_function(self, func_name, args=None):
        if self.director_env is None:
            raise Exception("[Erreur] Aucun 'director{}' déclaré dans ce programme")
        return self._call_in_env(self.director_env, func_name, args or [])

    def call_supervisor_function(self, name, func_name, args=None):
        sup = self.supervisors.get(name)
        if sup is None:
            raise Exception(f"[Erreur] Aucun supervisor nommé '{name}' (disponibles : {list(self.supervisors.keys())})")
        return self._call_in_env(sup["env"], func_name, args or [])

    def call_agent_function(self, name, func_name, args=None):
        ag = self.agent_blocks.get(name)
        if ag is None:
            raise Exception(f"[Erreur] Aucun agent nommé '{name}' (disponibles : {list(self.agent_blocks.keys())})")
        return self._call_in_env(ag["env"], func_name, args or [])

    def call_secretary_function(self, func_name, args=None):
        if self.secretary_env is None:
            raise Exception("[Erreur] Aucun 'secretary{}' déclaré dans ce programme")
        return self._call_in_env(self.secretary_env, func_name, args or [])

    def run_multi_agent(self, tache):
        """MultiAgent.run(tache) : fait circuler `tache` dans tout le sens du
        schéma — director -> supervisor -> agent -> secretary -> réponse ->
        agent -> supervisor -> director — et journalise chaque étape pour
        Monitor. Chaque rôle est optionnel : s'il ne définit pas la fonction
        attendue, l'étape est un simple passe-plat (la valeur traverse
        inchangée), pour ne jamais bloquer un programme partiellement écrit.

        Contrat de fonctions (toutes optionnelles) :
          director   : objectif(tache) -> tache_affinee
          supervisor : repartir(tache) -> sous_taches (liste)
                       agreger(resultats) -> resultat_agrege
          agent      : executer(sous_tache) -> resultat
          secretary  : repondre(reponse) -> reponse_finale
        """
        trace = OktopiosMap({})

        # --- DESCENTE : director -> supervisor -> agent ---
        tache_d = self.call_director_function("objectif", [tache])
        if tache_d is None:
            tache_d = tache
        trace.entries["director_descente"] = tache_d

        supervisor_results = []
        for sup_name in list(self.supervisors.keys()):
            sous_taches = self.call_supervisor_function(sup_name, "repartir", [tache_d])
            if sous_taches is None:
                sous_taches = [tache_d]
            elif not isinstance(sous_taches, (list, OktopiosList)):
                sous_taches = [sous_taches]

            agent_results = []
            agent_names = list(self.agent_blocks.keys()) or [None]
            for i, sous_tache in enumerate(sous_taches):
                agent_name = agent_names[i % len(agent_names)]
                if agent_name is None:
                    agent_results.append(sous_tache)  # aucun agent déclaré : passe-plat
                else:
                    resultat = self.call_agent_function(agent_name, "executer", [sous_tache])
                    agent_results.append(sous_tache if resultat is None else resultat)

            # --- MONTÉE : agent -> supervisor (agrégation) ---
            agrege = self.call_supervisor_function(sup_name, "agreger", [OktopiosList(agent_results)])
            supervisor_results.append(OktopiosList(agent_results) if agrege is None else agrege)

        trace.entries["agent_montee"] = OktopiosList(supervisor_results)

        # --- secretary : interface / réponse finale ---
        secretary_input = OktopiosList(supervisor_results) if supervisor_results else tache_d
        reponse = self.call_secretary_function("repondre", [secretary_input])
        if reponse is None:
            reponse = secretary_input
        trace.entries["secretary_reponse"] = reponse

        # --- MONTÉE finale : supervisor -> director ---
        director_final = self.call_director_function("collecter", [reponse])
        trace.entries["director_collecte"] = director_final if director_final is not None else reponse

        self.monitor_log([f"MultiAgent.run : {len(self.supervisors)} supervisor(s), {len(self.agent_blocks)} agent(s)"])

        final = director_final if director_final is not None else reponse
        return OktopiosMap({"reponse": final, "trace": trace})

    # ------------------------------------------------------------------
    # AdaptiveEngine : IAModule -> Analyse -> Décision -> Action -> Feedback
    # -> Apprentissage (MASTER_SPECIFICATION.md — Priorité n°2)
    # ------------------------------------------------------------------
    def _get_adaptive_memory(self):
        """Mémoire d'expérience : un neuron_loop dédié, créé à la première
        utilisation. L'apprentissage de l'AdaptiveEngine s'appuie donc sur le
        MÊME mécanisme __matches_db__ que le reste du langage."""
        if self.adaptive_memory_db is None:
            with self._shared_lock:
                if self.adaptive_memory_db is None:
                    db = NeuronLoopDB("AdaptiveMemory")
                    db.add_neuron(NeuroRuntime("neuro_1", enter={}, memory={}, elementor={}, out_blocks={}))
                    self.adaptive_memory_db = db
                    self.matches_db["AdaptiveMemory"] = db
        return self.adaptive_memory_db

    def adaptive_run(self, situation, options, backend="ollama", model=None, api_key=None):
        """AdaptiveEngine.run(situation, options) : IAModule -> Analyse ->
        Décision -> Action -> Feedback -> Apprentissage. Chaque étape est
        honnête sur son issue : si l'IA est indisponible, une heuristique de
        repli décide quand même (jamais de blocage), et le feedback le dit
        explicitement plutôt que de prétendre que l'IA a tranché."""
        options_list = list(options) if isinstance(options, (list, OktopiosList)) else [options]
        situation_str = str(situation)

        # --- IAModule : demande une décision à un modèle externe ---
        prompt = (
            f"Situation : {situation_str}\n"
            f"Options possibles : {', '.join(str(o) for o in options_list)}\n"
            "Choisis la meilleure option et explique brièvement pourquoi. "
            "Réponds STRICTEMENT au format : OPTION: <choix exact> | RAISON: <texte court>"
        )
        ia_response = None
        erreur_ia = None
        try:
            backend_fn = self.native_funcs.get("IAModule", {}).get(backend)
            if backend_fn is None:
                raise Exception(f"Backend IA inconnu : '{backend}'")
            if backend == "ollama":
                ia_response = backend_fn(prompt, model or "llama3")
            else:
                # deepseek/starcoder : api_key optionnelle (route vers Ollama
                # localement si absente — voir _ia_deepseek/_ia_starcoder)
                ia_response = backend_fn(prompt, api_key, model)
        except Exception as e:
            erreur_ia = str(e)

        # --- Analyse + Décision ---
        decision, raison = self._adaptive_parse_decision(ia_response, options_list)

        # --- Action : exécute agir(decision) si défini (core{} puis director{}) ---
        action_result = None
        if self.core_env is not None:
            action_result = self._call_in_env(self.core_env, "agir", [decision])
        if action_result is None and self.director_env is not None:
            action_result = self._call_in_env(self.director_env, "agir", [decision])

        # --- Feedback : honnête sur ce qui s'est réellement passé ---
        if erreur_ia:
            feedback = f"ia_indisponible: {erreur_ia}"
        elif action_result is not None:
            feedback = f"action_executee: {action_result}"
        else:
            feedback = "decision_seule (aucune fonction agir() definie dans core{} ou director{})"

        # --- Apprentissage : mémorise l'expérience pour AdaptiveEngine.recall() ---
        db = self._get_adaptive_memory()
        db.create_element("alpha", {
            "situation": situation_str,
            "decision": decision,
            "raison": raison,
            "feedback": feedback,
        })

        self.monitor_log([f"AdaptiveEngine.run : decision='{decision}' feedback='{feedback}'"])

        return OktopiosMap({
            "decision": decision,
            "raison": raison,
            "feedback": feedback,
            "action_result": action_result,
            "ia_response": ia_response,
            "erreur_ia": erreur_ia,
        })

    def _adaptive_parse_decision(self, ia_response, options):
        """Analyse + Décision : extrait OPTION/RAISON de la réponse IA. Si
        l'IA est indisponible ou répond hors-format, une heuristique de
        repli choisit quand même (jamais de blocage) — le feedback signale
        alors honnêtement que ce n'est pas l'IA qui a tranché."""
        if ia_response:
            option_choisie, raison_ia = None, None
            for part in str(ia_response).split("|"):
                part = part.strip()
                if part.upper().startswith("OPTION:"):
                    option_choisie = part.split(":", 1)[1].strip()
                elif part.upper().startswith("RAISON:"):
                    raison_ia = part.split(":", 1)[1].strip()
            if option_choisie:
                if option_choisie in options:
                    return option_choisie, raison_ia or "(IA)"
                sim_fn = self.native_funcs.get("Recognize", {}).get("textSimilarity")
                if sim_fn and options:
                    meilleure = max(options, key=lambda o: sim_fn(str(o), option_choisie))
                    return meilleure, raison_ia or "(IA, correspondance approchée)"
                return option_choisie, raison_ia or "(IA)"

        if options:
            return options[0], "repli heuristique (IA indisponible ou réponse non conforme)"
        return None, "aucune option fournie"

    def adaptive_recall(self, situation, threshold=1):
        """AdaptiveEngine.recall(situation) : réutilise EXACTEMENT le
        mécanisme __matches_db__ pour retrouver des expériences passées
        similaires — l'apprentissage et le rappel s'appuient sur la même
        mémoire associative que le reste du langage, pas un système séparé."""
        db = self._get_adaptive_memory()
        motif = [(Literal("situation"), ValuePattern(Literal(str(situation))))]
        with db.lock:
            matches = self._find_matches(db, str(situation), motif, max(0, threshold))
            return OktopiosList([
                self._entry_to_okp(n, s, c, r, e, fired=True, matched_criteria=cnt,
                                    threshold=threshold, propagation=[n])
                for n, s, c, r, e, cnt in matches
            ])

    def adaptive_memory_list(self):
        if self.adaptive_memory_db is None:
            return OktopiosList([])
        db = self.adaptive_memory_db
        with db.lock:
            return OktopiosList([
                OktopiosMap(e.to_okp_dict()) for n, s, c, r, e in db.all_locations()
            ])

    # ------------------------------------------------------------------
    # IAModule : fallback en cascade + streaming (MASTER_SPECIFICATION.md
    # — Priorité n°3 : timeout/reconnexion/streaming/fallback)
    # ------------------------------------------------------------------
    def ia_call_with_fallback(self, prompt, backends):
        """IAModule.callWithFallback(prompt, backends) : essaie chaque
        backend dans l'ordre donné jusqu'à ce qu'un réponde. Un appel IA qui
        échoue ne doit jamais planter un programme qui en a prévu un autre
        derrière — chaque échec est noté, pas juste avalé en silence."""
        backends_list = list(backends) if isinstance(backends, (list, OktopiosList)) else [backends]
        erreurs = []

        for cfg in backends_list:
            cfg = cfg.entries if isinstance(cfg, OktopiosMap) and cfg.entries is not None else dict(cfg)
            backend = cfg.get("backend", "ollama")
            fn = self.native_funcs.get("IAModule", {}).get(backend)
            if fn is None:
                erreurs.append(f"{backend}: backend inconnu")
                continue
            try:
                if backend == "ollama":
                    reponse = fn(
                        prompt, cfg.get("model", "llama3"), cfg.get("host", "http://localhost:11434"),
                        cfg.get("timeout", 60), cfg.get("retries", 2),
                    )
                else:
                    # deepseek/starcoder : api_key optionnelle (route vers
                    # Ollama localement si absente — voir _ia_deepseek/_ia_starcoder)
                    reponse = fn(
                        prompt, cfg.get("api_key"), cfg.get("model"),
                        cfg.get("timeout", 60), cfg.get("retries", 2), cfg.get("host", "http://localhost:11434"),
                    )
                return OktopiosMap({
                    "backend": backend,
                    "reponse": reponse,
                    "erreurs_precedentes": OktopiosList(erreurs),
                })
            except Exception as e:
                erreurs.append(f"{backend}: {e}")
                continue

        raise Exception(f"[IAModule.callWithFallback] Tous les backends ont échoué : {'; '.join(erreurs)}")

    def ia_ollama_stream(self, prompt, on_chunk, model="llama3", host="http://localhost:11434", timeout=60):
        """IAModule.ollamaStream(prompt, onChunk) : appelle onChunk(morceau)
        à chaque fragment reçu d'Ollama (garde la connexion 'vivante' sur les
        longues générations), et renvoie le texte complet à la fin."""
        def callback(piece):
            if isinstance(on_chunk, UserFunction):
                on_chunk.call(self, [piece])
        return _ia_ollama_stream(prompt, model, host, timeout, callback)

    def monitor_snapshot(self):
        """Heart 3 / Monitoring : état observable de l'organisme à l'instant T."""
        import time as _time
        return OktopiosMap({
            "horodatage": _time.time(),
            "tentacules": len(self.tentacles),
            "templates_tentacules": list(self.tentacle_templates.keys()),
            "hearts": list(self.hearts.keys()),
            "core_actif": self.core_env is not None,
            "taches_en_attente": len(self.task_queue),
            "bases_matches_db": list(self.matches_db.keys()),
            "evenements_logges": len(self.monitor_events),
        })

    def monitor_log(self, args):
        """Monitor.log(...) : trace un événement dans l'historique observable."""
        import time as _time
        message = " ".join(str(a) for a in args)
        event = OktopiosMap({"horodatage": _time.time(), "message": message})
        with self._shared_lock:
            self.monitor_events.append(event)
            return len(self.monitor_events)

    def save_matches_db(self, db_name, path):
        """MatchesDB.save('NomDB', 'chemin.json') : persiste une base
        neuron_loop sur disque (tout était perdu à la fin du programme)."""
        db = self.matches_db.get(db_name)
        if db is None:
            raise Exception(f"[Erreur] Aucune base __matches_db__ nommée '{db_name}'")
        db.save(path)
        return True

    def load_matches_db(self, db_name, path):
        """MatchesDB.load('NomDB', 'chemin.json') : recharge une base
        sauvegardée précédemment et l'enregistre sous ce nom."""
        db = NeuronLoopDB.load(path)
        db.name = db_name
        self.matches_db[db_name] = db
        self.env.define(db_name, db)
        return True

    def visit_IntentionStmt(self, stmt):
        args = [self.evaluate(arg) for arg in stmt.args]
        for tentacle in self.tentacles:
            self.dispatch_to_tentacle(tentacle, stmt.name, args, required=False)
        return None

    def visit_TentRandomStmt(self, stmt):
        args = [self.evaluate(arg) for arg in stmt.args]
        candidates = [tentacle for tentacle in self.tentacles if self.tentacle_has_method(tentacle, stmt.name, len(args))]
        if not candidates:
            return None
        self.dispatch_to_tentacle(random.choice(candidates), stmt.name, args, required=True)
        return None

    def tentacle_has_method(self, tentacle, name, arity=None):
        if arity is not None and f"{name}/{arity}" in tentacle.fieldsMeth:
            return True
        return name in tentacle.fieldsMeth

    def dispatch_to_tentacle(self, tentacle, name, args, required=False):
        if not self.tentacle_has_method(tentacle, name, len(args)):
            if required:
                raise Exception(f"[Erreur] Aucune methode '{name}/{len(args)}' dans la tentacule '{tentacle.klass.name}'")
            return None
        method = tentacle.get_method_bound(name, arg_count=len(args))
        return method.call(self, args)

    # ---- EXECUTION ----
    def execute(self, stmt: Stmt):
        #print(f"[DEBUG EXECUTE] type = {type(stmt).__name__}")
        # Gestion du pattern visitor pour les autres types de déclarations
        #print("ici dans execute ",stmt)
        method_name = f"visit_{type(stmt).__name__}"
        visitor = getattr(self, method_name, None)
        if visitor:
            return visitor(stmt)
        # Gestion du pattern visitor pour les déclarations de classe
        #elif isinstance(stmt, InterfaceDeclaration):
        #    print("ici dans execute ",stmt)
        #    return self.visit_InterfaceDeclaration(stmt)
        elif isinstance(stmt, EnumDeclaration):
            return self.visit_EnumDeclaration(stmt)
        #elif isinstance(stmt, ClassDeclaration):
        #    return self.visit_ClassDeclaration(stmt)
        elif isinstance(stmt, DeleteStmt):
            self.visit_Delete(stmt)
        elif isinstance(stmt, ActivateStmt):
            self.activate_class(stmt.class_name)
            return None
        elif isinstance(stmt, VarDecl):
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            else:
                value = default_value_for_type(stmt.type_)
            self.env.define(stmt.name, value=value, arity=None, is_constant=stmt.is_constant)
            return None
        elif isinstance(stmt, MultiVarDecl):
            for decl in stmt.decls:
                self.execute(decl)
            return None
        elif isinstance(stmt, PrintStmt):
            values = [self.evaluate(expr) for expr in stmt.expressions]

            def okp_str(v):
                if v is True:  return "true"
                if v is False: return "false"
                if v is None:  return "null"
                return str(v)

            output = " ".join(okp_str(v) for v in values)


            # kwargs
            color_code = ""
            if stmt.kwargs:
                color_name = stmt.kwargs.get("color")
                bg_name = stmt.kwargs.get("bg")
                style_name = stmt.kwargs.get("style")

                if color_name:
                    color_code += getattr(Fore, str(self.evaluate(color_name)).upper(), "")
                if bg_name:
                    color_code += getattr(Back, str(self.evaluate(bg_name)).upper(), "")
                if style_name:
                    color_code += getattr(Style, str(self.evaluate(style_name)).upper(), "")

            if color_code:
                with self._shared_lock:
                    print(f"{color_code}{output}{Style.RESET_ALL}")
            else:
                with self._shared_lock:
                    print(output)
            return None
        elif isinstance(stmt, IfStmt):
            if self.evaluate(stmt.condition):
                for s in stmt.then_branch:
                    self.execute(s)
                return None
            else:
                executed = False
                for elif_cond, elif_block in stmt.elif_branches:
                    if self.evaluate(elif_cond):
                        for s in elif_block:
                            self.execute(s)
                        executed = True
                        break
                if not executed and stmt.else_branch:
                    for s in stmt.else_branch:
                        self.execute(s)
                return None
        elif isinstance(stmt, SwitchStmt):
            switch_value = self.evaluate(stmt.expression)
            matched = False
            for case_value_expr, case_block in stmt.cases:
                case_value = self.evaluate(case_value_expr)
                if switch_value == case_value:
                    for s in case_block:
                        self.execute(s)
                    matched = True
                    break
            if not matched and stmt.default_block:
                for s in stmt.default_block:
                    self.execute(s)
            return None
        elif isinstance(stmt, WhileStmt):
            while self.evaluate(stmt.condition):
                try:
                    for s in stmt.body:
                        self.execute(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None
        elif isinstance(stmt, BlockStmt):
            previous = self.env
            self.env = Environment(enclosing=previous)
            try:
                for s in stmt.statements:
                    self.execute(s)
            finally:
                self.env = previous
        elif isinstance(stmt, ExpressionStmt):
            #print("Debug : dans interpreter ExpressionStmt : exec ", stmt.expression)
            if isinstance(stmt.expression, MethodCall):
                return self.execute(stmt.expression)
            self.evaluate(stmt.expression)
            return None
        elif isinstance(stmt, TryCatchFinallyStmt):
            try:
                for s in stmt.try_block:
                    self.execute(s)
            except Exception as e:
                if stmt.catch_block:
                    if stmt.error_var:
                        self.env.define(stmt.error_var, str(e))
                    for s in stmt.catch_block:
                        self.execute(s)
            finally:
                if stmt.finally_block:
                    for s in stmt.finally_block:
                        self.execute(s)
        elif isinstance(stmt, ThrowStmt):
            value = self.evaluate(stmt.expr)
            raise RuntimeError(str(value))
        elif isinstance(stmt, AugmentedAssign):
            print(stmt)
            current_value = self.env.get(stmt.name)
            increment = self.evaluate(stmt.value)
            op_type = stmt.operator.type
            if op_type == TokenType.PLUSEQ:
                new_value = current_value + increment
            elif op_type == TokenType.PLUS:
                new_value = current_value + 1
            elif op_type == TokenType.MINUSEQ:
                new_value = current_value - increment
            elif op_type == TokenType.MINUS:
                new_value = current_value - 1
            elif op_type == TokenType.STAREQ:
                new_value = current_value * increment
            elif op_type == TokenType.SLASHEQ:
                if increment == 0:
                    raise Exception(Fore.CYAN + "[Erreur] Division par zéro" + Style.RESET_ALL)
                new_value = current_value / increment
            else:
                raise Exception(
                    Fore.CYAN + f"[Erreur] Opérateur abrégé non supporté : {stmt.operator}" + Style.RESET_ALL)
            self.env.assign(stmt.name, new_value)
            return None
        elif isinstance(stmt, Assignment):
            value = self.evaluate(stmt.value)
            self.env.assign(stmt.name, value)

            return None
        elif isinstance(stmt, IndexThisAssignment):

            instance = self.evaluate(stmt.expr_this)

            container = instance.get_attr(stmt.expr_name, self)

            index = self.evaluate(stmt.index)
            value = self.evaluate(stmt.value)

            container.set(index, value)


            return value
        elif isinstance(stmt, FunDecl):
            func = UserFunction(stmt, self.env)
            self.env.define(stmt.name, value=func, arity=len(stmt.params))
            return None
        elif isinstance(stmt, ReturnStmt):
            #print(stmt.value)
            value = self.evaluate(stmt.value) if stmt.value else None
            raise ReturnValue(value)
        elif isinstance(stmt, ForEachStmt):
            iterable = self.evaluate(stmt.iterable_expr)
            if not hasattr(iterable, '__iter__'):
                raise Exception(
                    Fore.CYAN + f"[Erreur] '{stmt.var_name}' ne peut pas itérer sur : {type(iterable)}" + Style.RESET_ALL)

            for item in iterable:
                self.env.define(stmt.var_name, item)
                try:
                    for s in stmt.body:
                        self.execute(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return None
        # Affectation d'un attribut : ex. this.factor = 2  ou obj.attr = x
        elif isinstance(stmt, AttributeAssignment):
            # évaluer l'objet cible (this, variable contenant instance, etc.)
            obj = self.evaluate(stmt.obj_expr)


            # On n'autorise l'affectation d'attribut que sur des instances runtime
            if not isinstance(obj, (RuntimeInstance, RuntimeInstance_for_enum)):
                raise Exception(Fore.CYAN + f"[Erreur] Affectation d'attribut '{stmt.name}' sur un objet non-instancié ou non-objet : {obj}" + Style.RESET_ALL)

            # évaluer la valeur à affecter
            value = self.evaluate(stmt.value)

            # mettre à jour l'attribut sur l'instance
            obj.set_attr(stmt.name, value, self)
            return None
        elif isinstance(stmt, MethodCall):
            # Évaluer l'objet cible
            obj = self.evaluate(stmt.obj)
            #print("================ Debug : dans interpreter.entepreter MethodCall", obj)
            if isinstance(obj, RuntimeInstance):
                # Récupérer la méthode déclarée
                field_method = obj.fieldsMeth.get(stmt.method)
                if not field_method:
                    raise Exception(f"[Erreur] Méthode inconnue: {stmt.method}")

                # Ici field_method.methodeName est un FunDecl, il faut le transformer
                func_decl = field_method.methodeName
                user_func = UserFunction(func_decl, closure=None, instance=obj)

                # Évaluer les arguments
                args = [self.evaluate(arg) for arg in stmt.arguments]

                # Exécuter la méthode
                #print("Debug : dans interpreter MethodCall RuntimeInstance", user_func)
                return user_func.call(self, args)
            elif isinstance(obj, OktopiosMap):
                args = [self.evaluate(a) for a in stmt.arguments]
                return obj.callMethod(stmt.method, args)
            elif  isinstance(obj, OktopiosList) :
                variable = [self.evaluate(a) for a in stmt.arguments]
                obj.callMethod(method_name=stmt.method , args=variable)
                return None
            elif isinstance(obj, RuntimeClass):
                method = obj.get_static_method_bound(stmt.method, arg_count=len(stmt.arguments), line=stmt.line,
                                                     column=stmt.column)
                # Évaluer les arguments
                args = [self.evaluate(arg) for arg in stmt.arguments]

                # Exécuter la méthode
                #print("Debug : dans interpreter MethodCall RuntimeClass", method)
                return method.call(self, args, stmt.line, stmt.column)
            else:
                raise Exception(f"[Erreur] Tentative d'appel de méthode sur un objet invalide: {obj}")
        elif isinstance(stmt, ImportStmt):
            return self.visit_ImportStmt(stmt)
        elif isinstance(stmt, FromImportStmt):
            return self.visit_FromImportStmt(stmt)
        elif isinstance(stmt, UseStmt):
            return self.visit_UseStmt(stmt)
        elif isinstance(stmt, InjectStmt):
            #self.load_module(stmt.modules_with_alias, None)
            for module_name, alias in stmt.modules_with_alias:
                self.load_module(module_name, alias)
            return
        elif isinstance(stmt, BreakNode):
            raise BreakException()
        elif isinstance(stmt, ContinueNode):
            raise ContinueException()
        elif isinstance(stmt, SmartLoopStmt):
            return self.execute_loop_stmt(stmt)
        elif isinstance(stmt, PostfixIncrement):
            return self.evaluate_PostfixIncrement(stmt)
        elif isinstance(stmt, PostfixDecrement):
            return self.evaluate_PostfixDecrement(stmt)
        else:
            raise Exception(Fore.CYAN + f"[Erreur] Instruction non supportée: {stmt}" + Style.RESET_ALL)

    # ---- EVALUATION ----
    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Variable):
            value = self.env.get(expr.name, suppress_errors=True)
            if value is NOT_FOUND:
                value = self.global_env.get(expr.name, suppress_errors=True)
            if value is NOT_FOUND:
                # 🧠 Chercher dans les classes déclarées
                if expr.name in self.classes:
                    klass = self.classes[expr.name]
                    retrn =  RuntimeClass(klass, interpreter=self)
                    #print("ici retrn", retrn.name)
                    return retrn

            if value is NOT_FOUND:
                raise Exception(f"[Erreur] Variable ou fonction inconnue : {expr.name} dans la ligne: {expr.line} et colone: {expr.column}")
            #print(f"Donc value = {value}")
            return value
        #elif isinstance(expr, FunDecl) and expr.name is None:
        #    print("ici FunDecl intepreter", expr)
        #    return UserFunction(expr, self.env)  # 👈 closure capturée
        elif isinstance(expr, AnonymousFunction):
            return UserFunction(expr, self.env)
        elif isinstance(expr, FuncCall):
            #print("ici dans l'intepreter", expr)
            return  self.evaluate_func_call(expr)
        elif isinstance(expr, DictLiteral):
            evaluated_entries = {}
            #print("Debug 1: DictLiteral", expr.pairs)
            for key_expr, value_expr in expr.pairs:
                key_val = self.evaluate(key_expr)  # évaluation de la clé
                val = self.evaluate(value_expr)  # évaluation de la valeur
                evaluated_entries[key_val] = val
            return  OktopiosMap(evaluated_entries)

            #return  self.visit_DictLiteral(expr)
        elif isinstance(expr, MapUpdateCall):
            return  self.visit_UpadateDictLiteral(expr)
        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr)
        elif isinstance(expr, IsEmptyExpr):
            return self.visit_IsEmptyExpr(expr)
        elif isinstance(expr, MatchesExpr):
            return self.visit_MatchesExpr(expr)
        elif isinstance(expr, MatchExpr):
            return self.visit_MatchExpr(expr)
        elif isinstance(expr, MatchesDbExpr):
            return self.visit_MatchesDbExpr(expr)
        elif isinstance(expr, IsTypeExpr):
            return self.visit_IsTypeExpr(expr)
        elif isinstance(expr, BetweenExpr):
            return self.visit_BetweenExpr(expr)
        elif isinstance(expr, UnaryExpr):
            operand = self.evaluate(expr.operand)
            if expr.operator.type == TokenType.MINUS:
                return -operand
            elif expr.operator.type == TokenType.PLUS:
                return +operand
            else:
                raise Exception(Fore.CYAN + f"[Erreur] Opérateur unaire non supporté : {expr.operator.value}"+ Style.RESET_ALL)
        elif isinstance(expr, TernaryExpr):
            condition = self.evaluate(expr.condition)
            if condition:
                return self.evaluate(expr.then_expr)
            else:
                return self.evaluate(expr.else_expr)
        elif isinstance(expr, ListLiteral):
            variables = [self.evaluate(el) for el in expr.elements]

            return OktopiosList(variables)
        elif isinstance(expr, GetExpr):
            array = self.evaluate(expr.object)
            index = self.evaluate(expr.index)
            #print("tableau : ",array)
            #print(index)
            if isinstance(array, list):
                try:
                    return array[index]
                except IndexError:
                    raise RuntimeError(Fore.CYAN + "Index hors limites"+ Style.RESET_ALL)
            elif isinstance(array, OktopiosMap):
                try:
                    return array.get(index)
                except IndexError:
                    raise RuntimeError(Fore.CYAN + "Index hors limites"+ Style.RESET_ALL)
            #elif isinstance(array, DictLiteral):
            #    try:
            #        return array[index]
            #    except IndexError:
            #        raise RuntimeError(Fore.CYAN + "Index hors limites"+ Style.RESET_ALL)
            else:
                raise RuntimeError(Fore.CYAN + f"L'objet {expr} n'est pas indexable"+ Style.RESET_ALL)
        elif isinstance(expr, Assignment):
            value = self.evaluate(expr.value)
            #print(f"⚡ Assign {expr.name} -> {value} ({type(value)})")
            self.env.assign(expr.name, value)
            #print("Debug 2: ", value)
            return value
        elif isinstance(expr, AugmentedAssign):
            current_value = self.env.get(expr.name)
            increment = self.evaluate(expr.value)
            op_type = expr.operator.type
            #print("Debug 3: ", current_value, increment, op_type)
            from . native_collections import NativeCollectionsFuncs as NCF
            from . native_advanced_funcs import NativeAdvancedFuncs as NAF
            from . native_collections import ListInstance, TupleInstance, MapInstance, SetInstance
            from . native_advanced_collections import (
                LinkedListInstance,
                TreeSetInstance,
                LinkedHashSetInstance,
                TreeMapInstance,
                MatrixObject
            )
            from . matrix import Matrix

            # --- Gestion spéciale des collections ---
            if isinstance(current_value, ListInstance):
                if op_type == TokenType.PLUSEQ:
                    NCF["listExtend"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    NCF["listRemove"](current_value, increment)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour ListInstance : {op_type}")
            elif isinstance(current_value, SetInstance):
                if op_type == TokenType.PLUSEQ:
                    NCF["setUpdate"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    NCF["setDifferenceUpdate"](current_value, increment)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour SetInstance : {op_type}")
            elif isinstance(current_value, (MapInstance or dict)):
                if op_type == TokenType.PLUSEQ:
                    NCF["mapUpdate"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    if isinstance(increment, str):
                        NCF["mapPop"](current_value, increment)
                    else:
                        for key in increment:
                            NCF["mapPop"](current_value, key)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour MapInstance : {op_type}")
            elif isinstance(current_value, TupleInstance):
                if op_type == TokenType.PLUSEQ:
                    new_value = NCF["tupleJoin"](current_value, increment)
                elif op_type == TokenType.MINUSEQ:
                    new_value = NCF["tupleRemove"](current_value, increment)
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour TupleInstance : {op_type}")
            # =====================================================
            # --- Collections avancées ---
            # =====================================================
            elif isinstance(current_value, LinkedListInstance):
                if op_type == TokenType.PLUSEQ:
                    if isinstance(increment, (list, tuple)):
                        NAF["LinkedList"]["llAddAll"](current_value, increment)
                    else:
                        NAF["LinkedList"]["llAdd"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    for v in increment:
                        NAF["LinkedList"]["llRemove"](current_value, v)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour LinkedListInstance : {op_type}")
            elif isinstance(current_value, TreeSetInstance):
                if op_type == TokenType.PLUSEQ:
                    NAF["TreeSet"]["tsAddAll"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    for v in increment:
                        NAF["TreeSet"]["tsRemove"](current_value, v)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour TreeSetInstance : {op_type}")
            elif isinstance(current_value, LinkedHashSetInstance):
                if op_type == TokenType.PLUSEQ:
                    if isinstance(increment, (list, set, tuple)):
                        # Ajouter chaque élément individuellement
                        for v in increment:
                            NAF["LinkedHashSet"]["lhsAdd"](current_value, v)
                    else:
                        NAF["LinkedHashSet"]["lhsAdd"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    if isinstance(increment, (list, set, tuple)):
                        for v in increment:
                            NAF["LinkedHashSet"]["lhsRemove"](current_value, v)
                    else:
                        NAF["LinkedHashSet"]["lhsRemove"](current_value, increment)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour LinkedHashSetInstance : {op_type}")
            elif isinstance(current_value, TreeMapInstance):
                if op_type == TokenType.PLUSEQ:
                    NAF["TreeMap"]["tmPutAll"](current_value, increment)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    if isinstance(increment, str):
                        NAF["TreeMap"]["tmRemove"](current_value, increment)
                    else:
                        for key in increment:
                            NAF["treeMapRemove"](current_value, key)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération abrégée non supportée pour TreeMapInstance : {op_type}")

            # =====================================================
            # --- Matrix ---
            elif isinstance(current_value, MatrixObject):
                if op_type == TokenType.PLUSEQ:
                    if isinstance(increment, (list, tuple)) and len(increment) == 2:
                        coords, val = increment
                        current_value.set(coords, val)
                    new_value = current_value
                elif op_type == TokenType.MINUSEQ:
                    if isinstance(increment, (list, tuple)):
                        current_value.set(increment, None)
                    new_value = current_value
                else:
                    raise Exception(f"[Erreur] Opération non supportée pour MatrixObject : {op_type}")
            elif isinstance(current_value, Matrix):
                if op_type == TokenType.PLUSEQ:
                    if isinstance(increment, Matrix):
                        new_value = Matrix.add(current_value, increment)
                    else:
                        raise Exception("[Erreur] Matrix += nécessite une autre Matrix")
                else:
                    raise Exception(f"[Erreur] Opération non supportée pour Matrix : {op_type}")

            # --- Types simples ---
            # =====================================================

            else:
                # --- Cas classique : nombres, chaînes, etc. ---
                if op_type == TokenType.PLUSEQ:
                    new_value = current_value + increment
                elif op_type == TokenType.PLUS:
                    new_value = current_value + 1
                elif op_type == TokenType.MINUSEQ:
                    new_value = current_value - increment
                elif op_type == TokenType.MINUS:
                    new_value = current_value - 1
                elif op_type == TokenType.STAREQ:
                    new_value = current_value * increment
                elif op_type == TokenType.SLASHEQ:
                    if increment == 0:
                        raise Exception("[Erreur] Division par zéro")
                    new_value = current_value / increment
                else:
                    raise Exception(f"[Erreur] Opérateur abrégé non supporté : {expr.operator}")

            # Mise à jour de l’environnement
            self.env.assign(expr.name, new_value)
            return new_value
        elif isinstance(expr, LambdaExpr):
            return LambdaFunction(expr, self.env)
        elif isinstance(expr, NewInstanceExpr):
            class_decl = self.classes.get(expr.class_name)
            if not class_decl:
                raise Exception(f"[Erreur] Classe '{expr.class_name}' introuvable")

            # Évaluer les arguments avant l'instanciation
            #arg_values = [self.evaluate(arg) for arg in expr.arguments]
            instanceCreate = self.instantiate_class(class_decl, expr.arguments)
            return instanceCreate
        elif isinstance(expr, SuperCallExpr):
            # Assure que l'on est dans une instance
            if not hasattr(self, "current_instance") or self.current_instance is None:
                raise Exception("[Erreur] 'super' utilisé en dehors d'une instance")

            # parent_names peuvent être None ou liste de strings
            parent_names = expr.parent_names  # None ou list[str]
            # évaluer arguments
            args = [self.evaluate(arg) for arg in expr.arguments]
            # déléguer à RuntimeInstance.call_super
            return self.current_instance.call_super(expr.method_name, interpreter=self, args=args, parent_names=parent_names, caller_instance=self.current_instance)
        elif isinstance(expr, SuperForceCallExpr):
            if not self.current_instance:
                raise Exception("[Erreur] 'super_force' utilisé en dehors d'une instance de classe")

            results = []
            for parent_name in expr.parents:
                super_instance = self.current_instance.get_super_by_name(parent_name)
                if not super_instance:
                    raise Exception(f"[Erreur] Superclasse '{parent_name}' introuvable pour super_force")

                method = super_instance.get_method_bound(expr.method_name, caller_instance=self.current_instance)
                if not method:
                    raise Exception(f"[Erreur] Méthode '{expr.method_name}' introuvable dans {parent_name}")

                args = [self.evaluate(arg) for arg in expr.arguments]
                results.append(method.call(interpreter=self, args=args))

            # on retourne la liste des résultats (ou None si on veut ignorer)
            return results[-1] if results else None
        elif isinstance(expr, GetAttrExpr):
            instance = self.evaluate(expr.object_expr)
            attr_name = expr.name

            if not isinstance(instance, RuntimeInstance):
                raise Exception(f"[Erreur] Accès à l'attribut '{attr_name}' en dehors d'une instance de classe")

            return instance.get_attr(attr_name,self)
        elif isinstance(expr, MethodCallExpr):
            instance = self.evaluate(expr.object_expr)
            method = instance.get_method_bound(expr.method_name, caller_instance=self.current_instance)
            if not method:
                raise Exception(f"[Erreur] Méthode '{expr.method_name}' introuvable dans {instance.class_name}")
            args = [self.evaluate(arg) for arg in expr.arguments]
            return method.call(self, args)
        elif isinstance(expr, CallExpr):  # ou Call selon tes noms
            # évaluer la "fonction" ou la valeur callable
            callee = self.evaluate(expr.callee)
            # évaluer les arguments (valeurs)
            args = [self.evaluate(a) for a in expr.arguments]

            # cas 1 : fonction utilisateur (UserFunction)
            if isinstance(callee, UserFunction):
                return callee.call(self, args, line=getattr(expr, "line", None), column=getattr(expr, "column", None))

            # cas 2 : builtin enregistré comme callable Python
            if callable(callee):
                # On décide que les builtins reçoivent (interpreter, args)
                # Cela permet d'accéder à l'interpréteur si besoin.
                try:
                    return callee(self, args)
                except TypeError:
                    # si builtin a une signature différente, on tente sans passer interpreter
                    return callee(*args)

            # sinon erreur
            raise Exception(f"[Erreur] Appel sur une valeur non-callable : {callee}")
        elif isinstance(expr, ThisExpr):
            # On cherche 'this' dans l'environnement
            try:
                return self.env.get("this")
            except Exception:
                raise Exception("[Erreur] 'this' utilisé en dehors d'une instance")
        elif isinstance(expr, AttributeAccess):
            #print("Debug intepreter AttributeAccess :", expr.name)
            #print("Debug intepreter AttributeAccess :", expr.obj_expr)
            obj = self.evaluate(expr.obj_expr)

            # --- CAS INSTANCE D'ENUM (ex: Level.MEDIUM) ---
            if isinstance(obj, RuntimeInstance_for_enum):
                # Accès à une méthode définie sur le type d'enum
                enum_methods = getattr(obj.enum_type, "methods", [])
                # si la méthode existe, retourner la fonction bound
                for m in enum_methods:
                    if m.name == expr.name:
                        return obj.get_method_bound(expr.name, caller_instance=self.current_instance)
                # Accès à un champ stocké dans l'instance (this.name, champs initiaux)
                #print("obj.fields :", obj.fields)
                #print("expr.name :", expr.name)
                if expr.name in obj.fields:
                    # si tu stockes des Field objets, adapte .value ; ici on suppose valeur brute
                    return obj.fields[expr.name]
                raise Exception(f"[Erreur] '{expr.name}' introuvable dans la valeur d'enum '{obj}'")

            # 🔹 Cas Enum
            #print(obj)
            if isinstance(obj, RuntimeEnum):
                if expr.name in obj.values:
                    return obj.values[expr.name]
                else:
                    raise Exception(f"[Erreur] Valeur '{expr.name}' introuvable dans l'enum '{obj.name}'")

            #print(obj)
            if isinstance(obj, ModuleProxy):
                #print(f"Debug: dans intepreter accès à l’attribut '{expr.name}' dans le module {obj.module_name}")
                value = obj.__getattr__(expr.name)
                return value

            # --- CAS RuntimeClass : accès à variable ou méthode statique ---
            if isinstance(obj, RuntimeClass):
                if expr.name in obj.fields:
                    return obj.fields[expr.name].value

                # méthode statique
                if expr.name in obj.static_methods:
                    methst = obj.get_static_method_bound(expr.name)
                    #print("debug 1 AttributeAccess:  (obj, RuntimeClass) : ", methst)
                    return methst
                raise Exception(f"[Erreur] Membre statique '{expr.name}' introuvable dans la classe '{obj.name}'")

            if not isinstance(obj, RuntimeInstance):
                raise Exception(f"[Erreur] Accès attribut sur objet non valide: {obj}")

            # Vérifier s’il s’agit d’une variable (champ)
            #print(f'ci on teste le dictionnaire : {obj.fields}')
            if expr.name in obj.fields:
                field = obj.fields[expr.name]
                if field.access_modifier == "private" and obj != self.current_instance:
                    raise Exception(f"[Erreur] Accès illégal au champ privé '{expr.name}'")
                elif field.access_modifier == "protected" and obj != self.current_instance:
                    raise Exception(f"[Erreur] Accès illégal au champ protected '{expr.name}'")

                value = field.value


                # 🔥 sécurité anti-AST
                if isinstance(value, DictLiteral):
                    value = self.evaluate(value)
                    field.value = value  # remplacer définitivement
                    #print("1) ici = ", value)

                return value


            # Vérifier s’il s’agit d’une méthode
            if expr.name in obj.fieldsMeth:
                return obj.get_method_bound(expr.name, caller_instance=self.current_instance)

            raise Exception(f"[Erreur] Attribut ou méthode inconnu: {expr.name}")
        elif isinstance(expr, AttributeAssignment):
            obj = self.evaluate(expr.obj_expr) # this

            if isinstance(obj, RuntimeClass):
                value = self.evaluate(expr.value)
                obj.set_static_field(expr.name, value)
                return value

            if not isinstance(obj, RuntimeInstance):
                raise Exception(f"[Erreur] Affectation attribut '{expr.name}' en dehors d'une instance de classe")


            value = self.evaluate(expr.value)
            obj.set_attr(expr.name, value, from_this=isinstance(expr.obj_expr, ThisExpr))
            return value
        elif isinstance(expr, MethodCall):
            #print("================ Debug : dans interpreter.evaluate MethodCall", expr)
            obj = self.evaluate(expr.obj)  # RuntimeInstance/RuntimeClass
            args = [self.evaluate(arg) for arg in expr.arguments]
            arg_types = [self.get_type_name(a) for a in args]  # <— nouveau

            if isinstance(obj, RuntimeInstance):
                method = obj.get_method_bound(expr.method, caller_instance=self.current_instance, arg_types=arg_types, line=expr.line, column=expr.column)
                return method.call(self, args, expr.line, expr.column)
            elif isinstance(obj, RuntimeClass):
                method = obj.get_static_method_bound(expr.method, arg_count=len(expr.arguments), line=expr.line,
                                                     column=expr.column)
                # Évaluer les arguments
                args = [self.evaluate(arg) for arg in expr.arguments]

                # print("obj : ", method)
                # Exécuter la méthode
                return method.call(self, args, expr.line, expr.column)
            # Chercher la bonne méthode
            elif isinstance(obj, OktopiosMap):
                args = [self.evaluate(arg) for arg in expr.arguments]
                return obj.callMethod(expr.method, args)
            elif isinstance(obj, OktopiosList):
                args = [self.evaluate(arg) for arg in expr.arguments]
                return obj.callMethod(expr.method, args)
            elif isinstance(obj, (str, int, float, list, dict, tuple)):
                # Méthodes natives Python (ex: "texte".upper(), maListe.append(x))
                # pour les valeurs qui ne passent pas par OktopiosMap/OktopiosList.
                method_fn = getattr(obj, expr.method, None)
                if method_fn is None or not callable(method_fn):
                    raise Exception(f"[Erreur] Méthode inconnue : {type(obj).__name__}.{expr.method}({args})")
                try:
                    return method_fn(*args)
                except TypeError as e:
                    raise Exception(f"[Erreur] Appel invalide de {type(obj).__name__}.{expr.method}({args}) : {e}")
            else:
                raise Exception(f"[Erreur] Méthode inconnue : {type(obj).__name__}.{expr.method}({args})")
        elif isinstance(expr, ModuleFuncCall):
            #print(f'========== ModuleFuncCall {expr}')
            return self.evaluate_func_inject_call(expr)
        elif isinstance(expr, SetExpr):
            array = self.evaluate(expr.object)
            index = self.evaluate(expr.index)
            value = self.evaluate(expr.value)
            if isinstance(array, list):
                array[index] = value
                return value
            else:
                raise Exception(f"[Erreur] Objet non indexable pour SetExpr : {array}")
        elif isinstance(expr, VarDecl):
            # Évaluer la valeur initiale
            value = self.evaluate(expr.value) if expr.value else None
            print("value = ", value)

            # Vérifier la visibilité (public/private)
            visibility = getattr(expr, "visibility", expr.access_modifier)

            # Stocker dans l'environnement courant
            self.env.define(expr.name, value)
            return value
        elif isinstance(expr, IndexAccess):
            container = self.evaluate(expr.obj)
            index = self.evaluate(expr.index)
            #print(f" container : {container} ")
            #print(f" index : {index} ")

            # 🔹 Mise à jour réelle
            if isinstance(container, OktopiosMap):
                valeur = container.get(index)
            elif isinstance(container, dict):
                valeur = container.get(index)
            elif isinstance(container, OktopiosList):
                # liste : accès par index numérique
                if not isinstance(index, int):
                    raise Exception("[Erreur] L'index d'une liste doit être un entier")
                valeur = container.get(index)
            else:
                raise Exception(f"[Erreur] Type non indexable : {type(container).__name__}")
            return valeur
        elif isinstance(expr, IndexAssignment):
            # 🔹 Évaluer l’objet contenant
            if isinstance(expr.obj, Variable):
                var_name = expr.obj.name
                container = self.env.get(var_name)
            else:
                container = self.evaluate(expr.obj)
            # 🔹 Évaluer index et valeur
            index = self.evaluate(expr.index)
            value = self.evaluate(expr.value)
            #print(f"============== container : {container} ")
            #print(f"============== index : {index} ")
            # 🔹 Mise à jour réelle
            if isinstance(container, OktopiosMap):
                container.set(index, value)
            #elif isinstance(container, dict):
            #    container[index] = value
            elif isinstance(container, OktopiosList):
                container.set(index, value)
            #elif isinstance(container, list):
            #    # liste : accès par index numérique
            #    if not isinstance(index, int):
            #        raise Exception("[Erreur] L'index d'une liste doit être un entier")
            #    container[index] = value
            else:
                raise Exception(f"[Erreur] Type non indexable : {type(container).__name__}")


            return value
        elif isinstance(expr, RangeExpr):
            start = self.evaluate(expr.start)
            end = self.evaluate(expr.end)
            step = int(self.evaluate(expr.step)) if expr.step else 1

            if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
                raise Exception(
                    Fore.CYAN + "[Erreur] Les bornes de la plage doivent être numériques." + Style.RESET_ALL)

            if expr.operator == TokenType.LT:
                return range(int(start), int(end))  # Exclusif haut
            elif expr.operator == TokenType.GT:
                return range(int(start) + 1, int(end) + 1)  # Exclusif bas
            else:  # inclusif
                return range(int(start), int(end) + 1, step)
        elif isinstance(expr, FStringStmt):
            # Interpolation manuelle
            content = expr.value
            result = ""
            i = 0
            while i < len(content):
                if content[i] == '{':
                    end = content.find('}', i)
                    if end == -1:
                        raise Exception("Erreur de f-string : accolade fermante manquante")
                    expr_text = content[i + 1:end]
                    value = self.evaluate(self.parse_inline_expression(expr_text))
                    result += str(value)
                    i = end + 1
                else:
                    result += content[i]
                    i += 1
            return result
        elif isinstance(expr, PostfixIncrement):
            return self.evaluate_PostfixIncrement(expr)
        elif isinstance(expr, PostfixDecrement):
            return self.evaluate_PostfixDecrement(expr)
        #elif isinstance(expr, ExpressionStmt):
        #    print("Debug : dans interpreter ExpressionStmt eval : ", expr)
        #    if isinstance(expr.expression, BinaryOp):
        #        return self.evaluate(expr.expression)
        #    self.evaluate(expr.expression)
        #    return None
        else:
            raise Exception(Fore.CYAN + f"[Erreur] Expression non supporté : {expr} de type "+Fore.YELLOW+ f"{type(expr).__name__}"+ Style.RESET_ALL)

    # ---- ACTIVATION DES CLASSES ----
    def activate_class(self, class_name):
        # class_name peut être un token string ou un objet — normaliser en str
        if hasattr(class_name, "value"):
            cname = class_name.value
        else:
            cname = class_name

        if cname not in self.classes:
            raise Exception(Fore.CYAN + f"[Erreur] Classe '{cname}' introuvable pour activation" + Style.RESET_ALL)

        cls = self.classes[cname]

        # Créer une instance runtime (ton RuntimeInstance attend class_decl)
        instance = RuntimeInstance(cls)


        # Chercher la méthode 'main' dans l'instance
        main_func = instance.get_method_bound("main")
        if main_func:
            # main_func est une UserFunction (ou équivalent) ; l'appeler dans le contexte interpreter
            try:
                return main_func.call(self, [])
            except ReturnValue as rv:
                return rv.value
        else:
            print(Fore.YELLOW + f"[Info] Classe '{cname}' activée sans méthode main()" + Style.RESET_ALL)
            return None

    # ---- TYPE UTILS ----
    def normalize_type(self, type_name_or_value):
        """Renvoie un nom de type normalisé pour comparaison de types."""
        # Si on reçoit une instance (et pas une string)
        #print(type_name_or_value)
        #print(isinstance(type_name_or_value, str))
        if isinstance(type_name_or_value, str):
            val = type_name_or_value

            # 🔹 Cas des enums
            #print(val)
            if isinstance(val, RuntimeInstance_for_enum):
                return val.enum_type.name  # ex: "Color"

            # 🔹 Cas des classes normales
            if hasattr(val, "klass") and hasattr(val.klass, "name"):
                return val.klass.name

            # 🔹 Fallback standard
            return type(val).__name__

        # Sinon, on normalise une chaîne
        t = type_name_or_value.lower()
        mapping = {
            "string": "string",
            "str": "string",
            "int": "int",
            "integer": "int",
            "float": "float",
            "double": "float",
            "bool": "bool",
            "boolean": "bool",
            "void": "void",
        }
        return mapping.get(t, type_name_or_value)

    def infer_type(self, value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            if not value:
                return "unknown[]"  # liste vide
            elem_type = self.infer_type(value[0])
            if all(self.infer_type(v) == elem_type for v in value):
                return f"{elem_type}[]"
            else:
                return "mixed[]"
        else:
            return "unknown"

    def type_matches(self, expected_type, value):
        actual_type = self.infer_type(value)
        if expected_type == actual_type:
            return True
        if expected_type.endswith("[]") and actual_type.endswith("[]"):
            return expected_type == actual_type
        return False

    # ---------------------------
    # Résolution de l'héritage et validation
    # ---------------------------
    def resolve_inheritance_and_validate(self):
        """
        Résout les superclasses, classes abstraites et interfaces :
        ✅ Connecte les classes parentes
        ✅ Vérifie les overrides et invokes
        ✅ Assure la conformité des interfaces
        ✅ Transmet les méthodes statiques des parents (héritage statique à la C++/Java)
        """

        # ------------------------
        # 1️⃣ Résolution des classes et classes abstraites
        # ------------------------
        all_classes = list(self.classes.values()) + list(self.abstract_classes.values())

        for cls in all_classes:
            # ---- Résolution des superclasses ----
            if getattr(cls, "superclass", None):
                parents = cls.superclass if isinstance(cls.superclass, list) else [cls.superclass]
                resolved_parents = []
                for p_name in parents:
                    parent_cls = self.classes.get(p_name) or self.abstract_classes.get(p_name)
                    if not parent_cls:
                        raise Exception(f"[Erreur] Superclasse '{p_name}' introuvable pour '{cls.name}'")
                    resolved_parents.append(parent_cls)
                cls.superclass = resolved_parents

            # ---- Résolution des interfaces ----
            if getattr(cls, "interfaces", None):
                resolved_interfaces = []
                for iface_name in cls.interfaces:
                    iface_ast = self.interfaces.get(iface_name)
                    if not iface_ast:
                        raise Exception(f"[Erreur] Interface '{iface_name}' introuvable pour '{cls.name}'")
                    resolved_interfaces.append(iface_ast)
                cls.interfaces = resolved_interfaces

            # ---- Collecte des méthodes héritées (instance uniquement) ----
            inherited_methods = {}

            def collect_methods_from_parent(parent):
                """Collecte récursive des méthodes des classes et interfaces parentes."""
                if isinstance(parent, InterfaceDeclaration):
                    parent_methods = parent.methods
                else:
                    parent_methods = getattr(parent, "members", [])

                for m in parent_methods:
                    if isinstance(m, FunDecl) and m.name not in inherited_methods:
                        inherited_methods[m.name] = m
                        m.parent = parent

                # Récursion : classes parentes
                if hasattr(parent, "superclass") and parent.superclass:
                    for sp in parent.superclass:
                        collect_methods_from_parent(sp)

                # Récursion : interfaces parentes
                if isinstance(parent, InterfaceDeclaration) and getattr(parent, "super_interfaces", None):
                    for super_iface in parent.super_interfaces:
                        if isinstance(super_iface, str):
                            resolved = self.interfaces.get(super_iface)
                            if not resolved:
                                raise Exception(
                                    f"[Erreur] Super-interface '{super_iface}' introuvable pour '{parent.name}'"
                                )
                            collect_methods_from_parent(resolved)
                        else:
                            collect_methods_from_parent(super_iface)

            # ---- Collecte depuis superclasses et interfaces ----
            if getattr(cls, "superclass", None):
                for parent in cls.superclass:
                    collect_methods_from_parent(parent)

            if getattr(cls, "interfaces", None):
                for iface in cls.interfaces:
                    collect_methods_from_parent(iface)

            # ---- Vérification des overrides et invoke ----
            if isinstance(cls, ClassDeclaration):
                for member in cls.members:
                    if isinstance(member, FunDecl) and member.name in inherited_methods:
                        parent_method = inherited_methods[member.name]

                        # Hérité d’une classe
                        if isinstance(parent_method.parent, ClassDeclaration):
                            if not getattr(member, "is_override", False) and not getattr(member, "is_construct", False):
                                raise Exception(
                                    f"[Erreur] La méthode '{member.name}' de '{cls.name}' existe déjà dans une classe parente "
                                    f"('{parent_method.parent.name}'). Précédez-la de 'override' pour redéfinir."
                                )

                        # Hérité d’une interface
                        elif isinstance(parent_method.parent, InterfaceDeclaration):
                            if not getattr(member, "is_invoke", False):
                                raise Exception(
                                    f"[Erreur] La méthode '{member.name}' de '{cls.name}' implémente une interface "
                                    f"('{parent_method.parent.name}') et doit être précédée de 'invoke'."
                                )

            # ---- 🔥 NOUVEAUTÉ : héritage des méthodes statiques ----
            if isinstance(cls, ClassDeclaration):
                # On s'assure que chaque classe a bien un dictionnaire de méthodes statiques
                cls.static_methods = getattr(cls, "static_methods", {})

                # Pour chaque parent, on propage les méthodes statiques non redéfinies
                for parent in getattr(cls, "superclass", []) or []:
                    parent_static = getattr(parent, "static_methods", {})
                    for name, method in parent_static.items():
                        if name not in cls.static_methods:
                            cls.static_methods[name] = method

        # ------------------------
        # 2️⃣ Résolution des super-interfaces
        # ------------------------
        for iface in self.interfaces.values():
            if getattr(iface, "super_interfaces", None):
                resolved_supers = []
                for super_name in iface.super_interfaces:
                    super_iface = self.interfaces.get(super_name)
                    if not super_iface:
                        raise Exception(f"[Erreur] Super-interface '{super_name}' introuvable pour '{iface.name}'")
                    resolved_supers.append(super_iface)
                iface.super_interfaces = resolved_supers

    # ---------------------------
    # Vérification que toutes les classes concrètes respectent les contrats d'interfaces
    # ---------------------------
    def validate_interface_contracts(self):
        """
        Vérifie que toutes les classes concrètes implémentent toutes les méthodes
        de leurs interfaces (directes et héritées).
        """
        for cls_name, cls in self.classes.items():  # uniquement classes concrètes
            if not getattr(cls, 'interfaces', None):
                continue

            implemented_method_names = {m.name for m in cls.members if isinstance(m, FunDecl)}

            for iface in cls.interfaces:
                # Collecter toutes les méthodes y compris celles des super-interfaces
                def collect_interface_methods(interface):
                    methods = list(interface.methods)
                    for super_iface in getattr(interface, "super_interfaces", []):
                        methods.extend(collect_interface_methods(super_iface))
                    return methods

                required_methods = collect_interface_methods(iface)

                for req_method in required_methods:
                    if req_method.name not in implemented_method_names:
                        raise Exception(
                            f"[Erreur] La classe '{cls.name}' implémente l'interface '{iface.name}' "
                            f"mais la méthode requise '{req_method.name}()' est manquante."
                        )

    def Visite_Function_declar(self, program):
        for stmt in program.body:
            if isinstance(stmt, FunDecl):
                func = UserFunction(stmt, self.env)

                # Construire la signature des paramètres
                param_types = [ptype for (_, ptype, _, _) in stmt.params]
                type_signature = ",".join(param_types)

                # Enregistrer avec signature complète
                full_key = f"{stmt.name}/{len(stmt.params)}/{type_signature}"
                self.env.define(full_key, func)

                # Garder aussi un enregistrement simple pour les appels sans vérification
                # (optionnel, pour compatibilité)
                self.env.define(stmt.name, value=func, arity=len(stmt.params))

    def visit_EnumDeclaration(self, stmt):
        enum_obj = RuntimeEnum(
            name=stmt.name,
            values={},
            fields=stmt.fields,
            methods=stmt.methods,
            interpreter=self
        )

        # Création de chaque constante avec son indice ordinal
        for i, (const_name, args) in enumerate(stmt.values):
            instance = RuntimeInstance_for_enum(enum_obj, const_name, interpreter=self, ordinal=i)

            # Appel de init() si défini
            init_method = next((m for m in stmt.methods if m.name == "__construct"), None)
            if init_method:
                eval_args = [self.evaluate(a) for a in args]
                # ici, on passe l'instance comme "this"
                self.call_function(init_method, eval_args, instance)

            enum_obj.values[const_name] = instance
            self.env.define(f"{stmt.name}.{const_name}", instance)

        self.env.define(stmt.name, enum_obj)
        self.enums[stmt.name] = enum_obj
        return None

    def call_function(self, function_decl, args, instance=None):
        env_backup = self.env
        call_env = Environment(parent=self.env)

        if instance:
            call_env.define("this", instance)

        # Boucle sur les paramètres
        for i, (param_name, param_type, is_const, extra) in enumerate(function_decl.params):
            #print(f"Debug param: {param_name}, extra={extra}, args={args}")

            if i < len(args):
                # Argument fourni par l'appel
                value = args[i]
            else:
                # Gestion des valeurs par défaut
                if isinstance(extra, Literal):
                    # Si extra est un Literal, on utilise sa valeur directement
                    value = self.evaluate(extra)
                elif extra and isinstance(extra, dict) and "default" in extra:
                    value = self.evaluate(extra["default"])
                else:
                    raise Exception(
                        f"[Erreur] Argument manquant pour le paramètre '{param_name}' dans {function_decl.name}"
                    )

            call_env.define(param_name, value)

        # Exécution du corps
        self.env = call_env
        try:
            self.execute_block(function_decl.body, call_env)
        finally:
            self.env = env_backup

    def instantiate_class(self, class_decl, args=None):
        args = args or []
        instance = RuntimeInstance(class_decl, constructor_args=args, interpreter=self)

        # --- Helper : créer/binder un UserFunction depuis FunDecl ou depuis RuntimeClass.methods entry
        def make_bound_userfunction(maybe_decl_or_userfunc, owner=None):
            # Si c'est déjà un UserFunction (ex: RuntimeClass.methods stocke UserFunction), binder si besoin
            from . user_function import UserFunction
            if isinstance(maybe_decl_or_userfunc, UserFunction):
                # s'assurer qu'il est bound à l'instance (UserFunction garde instance dans son champ)
                # si instance déjà présent, on le retourne ; sinon on crée un nouveau bound
                if getattr(maybe_decl_or_userfunc, "instance", None) is instance:
                    return maybe_decl_or_userfunc
                # recréer un UserFunction bound (préserver native/decl)
                return UserFunction(maybe_decl_or_userfunc.declaration or maybe_decl_or_userfunc.native,
                                    maybe_decl_or_userfunc.closure,
                                    instance=instance)
            # sinon on suppose un FunDecl AST — utilise le closure de la classe qui définit
            # réellement la méthode (owner), important pour les méthodes héritées
            owner_decl = owner if owner is not None else class_decl
            return UserFunction(maybe_decl_or_userfunc, getattr(owner_decl, "closure", None), instance=instance)

        # --- Trouver constructeur / destructeur (s'adapte si class_decl est AST ou RuntimeClass)
        # Remonte la chaîne des superclasses si la classe elle-même n'en définit pas
        # (sinon une classe enfant sans __construct utilisait un constructeur vide
        # et perdait silencieusement les arguments passés à 'new Enfant(...)').
        def find_method_owner(decl, method_name, visited=None):
            visited = visited if visited is not None else set()
            if id(decl) in visited:
                return None, None
            visited.add(id(decl))

            if hasattr(decl, "methods") and isinstance(decl.methods, dict):
                found = decl.methods.get(method_name)
                if found is not None:
                    return found, decl
            else:
                found = next((m for m in getattr(decl, "methods", []) if m.name == method_name), None)
                if found is not None:
                    return found, decl

            for parent in (getattr(decl, "superclass", None) or []):
                m, owner = find_method_owner(parent, method_name, visited)
                if m is not None:
                    return m, owner
            return None, None

        constructor_decl, constructor_owner = find_method_owner(class_decl, "__construct")
        destructor_decl, destructor_owner = find_method_owner(class_decl, "__destruct")

        # --- Normaliser et stocker un UserFunction bound pour le constructeur
        if constructor_decl is not None:
            bound_ctor = make_bound_userfunction(constructor_decl, owner=constructor_owner)
            instance.fieldsMeth["__construct"] = bound_ctor
        else:
            # constructeur par défaut (callable Python simple)
            def default_constructor(*_args, **_kwargs):
                #if DEBUG:
                #    print(f"[DEBUG] Constructeur par défaut exécuté pour {getattr(class_decl, 'name', '<anon>')}")
                return None

            instance.fieldsMeth["__construct"] = default_constructor

        # --- Normaliser et stocker un UserFunction bound pour le destructeur
        if destructor_decl is not None:
            bound_dtor = make_bound_userfunction(destructor_decl, owner=destructor_owner)
            instance.fieldsMeth["__destruct"] = bound_dtor
        else:
            def default_destructor():
                #if DEBUG:
                #    print(f"[DEBUG] Destructeur par défaut exécuté pour {getattr(class_decl, 'name', '<anon>')}")
                # simulation de libération mémoire
                if hasattr(instance, "fields"):
                    instance.fields.clear()
                if hasattr(instance, "fieldsMeth"):
                    instance.fieldsMeth.clear()

            instance.fieldsMeth["__destruct"] = default_destructor

        # --- Appel automatique du constructeur (toujours, même sans arguments —
        #     un constructeur à zéro paramètre doit quand même s'exécuter)
        evaluated_args = []
        if self is not None:
            evaluated_args = [
                self.evaluate(a) if not isinstance(a, (int, float, str, bool, list)) else a
                for a in args
            ]
        else:
            evaluated_args = args

        ctor = instance.fieldsMeth.get("__construct")
        if isinstance(ctor, UserFunction):
            ctor.call(self, evaluated_args)
        elif callable(ctor):
            ctor(*evaluated_args)

        # --- Enregistrement de destruction automatique (façon faibles références)
        #import weakref
        #def _auto_cleanup(wref):
        #    try:
        #        dest = instance.fieldsMeth.get("__destruct")
        #        if dest:
        #            if isinstance(dest, UserFunction):
        #                dest.call(interpreter=self, args=[])  # appeler bound UserFunction sans args
        #            elif callable(dest):
        #                dest()
        #    except Exception as e:
        #        print(
        #            f"[Erreur lors de l'appel du destructeur automatique de {getattr(class_decl, 'name', '<anon>')}]: {e}")

        #weakref.finalize(instance, _auto_cleanup, weakref.ref(instance))
        return instance

    def evaluate_PostfixIncrement(self, expr):
        old = self.env.get(expr.name)
        self.env.assign(expr.name, old + 1)
        return old  # valeur retournée

    def evaluate_PostfixDecrement(self, expr):
        old = self.env.get(expr.name)
        self.env.assign(expr.name, old - 1)
        return old

    # interpreter.py (méthode pour exécuter SmartLoopStmt / LoopStmt)
    def execute_loop_stmt(self, stmt: LoopStmt):
        kind = stmt.kind
        iterable = self.evaluate(stmt.iterator) if stmt.iterator else range(0, 10)

        # --- LOOP: when or simple
        if kind == "Loop":
            cond_exprs = stmt.modifiers.get("when", [])

        # --- FILTER LOOP : where + then ---
        if kind == "filterLoop":
            cond_exprs = stmt.modifiers.get("where", [])
            then_exprs = stmt.modifiers.get("then", None)

            # Uniformiser : liste si un seul where
            if not isinstance(cond_exprs, list):
                cond_exprs = [cond_exprs]

            filtered = []
            for x in iterable:
                self.env.define(stmt.var_name, x)

                # Tous les "where" doivent être vrais
                ok_all = all(self.eval_condition(expr, {stmt.var_name: x}) for expr in cond_exprs)

                if ok_all:
                    # Si on a un THEN (ex: exécution d’un effet avant le corps)
                    if then_exprs:
                        if isinstance(then_exprs, list):
                            for te in then_exprs:
                                self.evaluate(te)
                        else:
                            self.evaluate(then_exprs)

                    filtered.append(x)

            iterable = filtered

        # --- FILTER WHILE ---
        if kind == "filterWhile":

            cond_exprs = stmt.modifiers.get("whenever", [])
            check_exprs = stmt.modifiers.get("check", [])

            # Toujours travailler en listes
            if not isinstance(cond_exprs, list):
                cond_exprs = [cond_exprs]
            if not isinstance(check_exprs, list):
                check_exprs = [check_exprs]

            filtered = []

            for x in iterable:
                # injecter la variable (ex: i)
                self.env.define(stmt.var_name, x)

                # Vérifier les whenever : tous doivent être True
                ok_all = True
                for expr in cond_exprs:
                    if not self.evaluate(expr):
                        ok_all = False
                        break

                if not ok_all:
                    continue  # on rejette immédiatement

                # --- CHECK(...) présent ? ---
                if len(check_exprs) > 0:

                    # Au moins un check doit être vrai
                    ok_check = False
                    for expr in check_exprs:
                        if self.evaluate(expr):
                            ok_check = True
                            break

                    if ok_check:
                        filtered.append(x)

                # --- PAS DE CHECK → on accepte directement ---
                else:
                    filtered.append(x)

            iterable = filtered

        # --- SORT LOOP ---
        if kind == "sortLoop":
            if "by" in stmt.modifiers:
                key_expr = stmt.modifiers["by"]
                order = stmt.modifiers.get("order", "asc")
                iterable = sorted(
                    iterable,
                    key=lambda x: self.eval_in_context(key_expr, {stmt.var_name: x}),
                    reverse=(order == "desc")
                )

        # --- PERMUTE LOOP ---
        if kind == "permuteLoop":

            items = list(self.evaluate(stmt.iterator))
            if not isinstance(items, list):
                raise RuntimeError("[Erreur] 'permuteLoop' ne peut s'appliquer qu'à des listes.")

            using_vars = stmt.modifiers.get("using", []) or []
            mode = stmt.modifiers.get("mode", "random")
            where_exprs = stmt.modifiers.get("where", []) or []

            length = len(items)
            length_where = len(where_exprs)
            if length == 0:
                return
            if "where" in stmt.modifiers and length_where == 0 :
                raise RuntimeError(f"[Erreur] 'where' n'a pas d'utilité sans parametres")


            import random

            # ---------------------------------------
            # MODE : préparation base_items
            # ---------------------------------------
            base_items = items[:]

            if mode == "stable":
                pass

            elif mode == "reverse":
                base_items.reverse()

            elif mode == "cycle":
                base_items = base_items[1:] + base_items[:1]

            elif mode == "chaos":
                pass  # shuffle à chaque tour plus bas

            elif mode == "noise":
                for i in range(len(base_items) - 1):
                    if random.random() < 0.35:
                        base_items[i], base_items[i + 1] = base_items[i + 1], base_items[i]

            elif mode == "random":
                random.shuffle(base_items)

            else:
                raise RuntimeError(f"[Erreur] Mode inconnu dans permuteLoop : {mode}")

            # ----------------------------------------------------------
            # CAS SANS USING(...)
            # ----------------------------------------------------------
            if not using_vars:

                for idx in range(length):

                    saved_env = self.env
                    local_env = Environment(enclosing=saved_env)
                    self.env = local_env

                    try:
                        if mode == "chaos":
                            tmp = base_items[:]
                            random.shuffle(tmp)
                            v = tmp[0]
                        else:
                            v = base_items[idx]

                        self.env.define(stmt.var_name, v)

                        # --- WHERE (uniquement "n") ---
                        ok = True
                        for expr in where_exprs:
                            if not self.evaluate(expr):
                                ok = False
                                break

                        if ok:
                            for s in stmt.body:
                                self.execute(s)

                    finally:
                        self.env = saved_env

                return

            # ----------------------------------------------------------
            # CAS AVEC USING(...)
            # ----------------------------------------------------------
            for idx_base in range(length):

                saved_env = self.env
                local_env = Environment(enclosing=saved_env)
                self.env = local_env

                try:
                    # valeur principale n
                    self.env.define(stmt.var_name, base_items[idx_base])

                    # positions secondaires
                    secondary_indices = [(idx_base + k + 1) % length for k in range(len(using_vars))]

                    # appliquer mode sur secondary_indices
                    if mode == "reverse":
                        secondary_indices.reverse()

                    elif mode == "cycle":
                        secondary_indices = secondary_indices[1:] + secondary_indices[:1]

                    elif mode == "chaos":
                        random.shuffle(secondary_indices)

                    elif mode == "noise":
                        for i in range(len(secondary_indices) - 1):
                            if random.random() < 0.35:
                                secondary_indices[i], secondary_indices[i + 1] = (
                                    secondary_indices[i + 1],
                                    secondary_indices[i]
                                )

                    elif mode == "random":
                        random.shuffle(secondary_indices)

                    # assigner using(...)
                    for k, name in enumerate(using_vars):
                        pos = secondary_indices[k]
                        self.env.define(name, base_items[pos])

                    # --- WHERE : vérifier AVANT l'exécution ---
                    ok = True
                    for expr in where_exprs:
                        if not self.evaluate(expr):
                            ok = False
                            break

                    if ok:
                        for s in stmt.body:
                            self.execute(s)

                finally:
                    self.env = saved_env

            return

        # --- PERMUTE While ---
        if kind == "permuteWhile":

            items = list(self.evaluate(stmt.iterator))
            if not isinstance(items, list):
                raise RuntimeError("[Erreur] 'permuteLoop' ne peut s'appliquer qu'à des listes.")

            using_vars = stmt.modifiers.get("using", []) or []
            mode = stmt.modifiers.get("mode", "random")
            where_exprs = stmt.modifiers.get("where", []) or []

            length = len(items)
            length_where = len(where_exprs)
            if length == 0:
                return
            if "where" in stmt.modifiers and length_where == 0 :
                raise RuntimeError(f"[Erreur] 'where' n'a pas d'utilité sans parametres")


            import random

            # ---------------------------------------
            # MODE : préparation base_items
            # ---------------------------------------
            base_items = items[:]

            if mode == "stable":
                pass

            elif mode == "reverse":
                base_items.reverse()

            elif mode == "cycle":
                base_items = base_items[1:] + base_items[:1]

            elif mode == "chaos":
                pass  # shuffle à chaque tour plus bas

            elif mode == "noise":
                for i in range(len(base_items) - 1):
                    if random.random() < 0.35:
                        base_items[i], base_items[i + 1] = base_items[i + 1], base_items[i]

            elif mode == "random":
                random.shuffle(base_items)

            else:
                raise RuntimeError(f"[Erreur] Mode inconnu dans permuteLoop : {mode}")

            # ----------------------------------------------------------
            # CAS SANS USING(...)
            # ----------------------------------------------------------
            if not using_vars:

                for idx in range(length):

                    saved_env = self.env
                    local_env = Environment(enclosing=saved_env)
                    self.env = local_env

                    try:
                        if mode == "chaos":
                            tmp = base_items[:]
                            random.shuffle(tmp)
                            v = tmp[0]
                        else:
                            v = base_items[idx]

                        self.env.define(stmt.var_name, v)

                        # --- WHERE (uniquement "n") ---
                        ok = True
                        for expr in where_exprs:
                            if not self.evaluate(expr):
                                ok = False
                                break

                        if ok:
                            for s in stmt.body:
                                self.execute(s)

                    finally:
                        self.env = saved_env

                return

            # ----------------------------------------------------------
            # CAS AVEC USING(...)
            # ----------------------------------------------------------
            for idx_base in range(length):

                saved_env = self.env
                local_env = Environment(enclosing=saved_env)
                self.env = local_env

                try:
                    # valeur principale n
                    self.env.define(stmt.var_name, base_items[idx_base])

                    # positions secondaires
                    secondary_indices = [(idx_base + k + 1) % length for k in range(len(using_vars))]

                    # appliquer mode sur secondary_indices
                    if mode == "reverse":
                        secondary_indices.reverse()

                    elif mode == "cycle":
                        secondary_indices = secondary_indices[1:] + secondary_indices[:1]

                    elif mode == "chaos":
                        random.shuffle(secondary_indices)

                    elif mode == "noise":
                        for i in range(len(secondary_indices) - 1):
                            if random.random() < 0.35:
                                secondary_indices[i], secondary_indices[i + 1] = (
                                    secondary_indices[i + 1],
                                    secondary_indices[i]
                                )

                    elif mode == "random":
                        random.shuffle(secondary_indices)

                    # assigner using(...)
                    for k, name in enumerate(using_vars):
                        pos = secondary_indices[k]
                        self.env.define(name, base_items[pos])

                    # --- WHERE : vérifier AVANT l'exécution ---
                    ok = True
                    for expr in where_exprs:
                        if not self.evaluate(expr):
                            ok = False
                            break

                    if ok:
                        for s in stmt.body:
                            self.execute(s)

                finally:
                    self.env = saved_env

            return

        # --- CIRCULAR LOOP ---
        if kind == "circularLoop":
            iterable = list(iterable)
            if not iterable:
                return

            index = 0
            step = 1

            # Si un "step" est défini dans les modificateurs
            if "step" in stmt.modifiers:
                step_expr = stmt.modifiers["step"]
                step = int(self.evaluate(step_expr))

            # Optionnel : condition d’arrêt (until)
            until_cond = stmt.modifiers.get("until", None)

            # Boucle infinie jusqu’à break ou until
            while True:

                item = iterable[index % len(iterable)]
                self.env.define(stmt.var_name, item)

                try:
                    for s in stmt.body:
                        self.execute(s)
                except BreakException:
                    break
                except ContinueException:
                    pass

                # condition d’arrêt
                if until_cond is not None:
                    if self.eval_condition(until_cond, {stmt.var_name: item}):
                        break

                index += step
            return  # bug trouvé en testant : sans ce return, on retombait dans
                     # la "BOUCLE STANDARD" plus bas et on ré-itérait en plus


        # --- SLEEPING LOOP ---
        if kind == "sleepingLoop" and "waitUntil" in stmt.modifiers:
            cond_expr = stmt.modifiers["waitUntil"]
            import time
            while not self.evaluate(cond_expr):
                time.sleep(0.05)

        # --- LOOP MATRIX ---
        if kind == "loopMatrix":
            matrix_obj = self.evaluate(stmt.iterator)
            if not hasattr(matrix_obj, "width") or not hasattr(matrix_obj, "height"):
                raise RuntimeError("loopMatrix attend un objet Matrix avec width et height.")

            for i in range(matrix_obj.height):
                for j in range(matrix_obj.width):
                    cell = matrix_obj[i][j] if hasattr(matrix_obj, "__getitem__") else (i, j)
                    self.env.define(stmt.var_name, cell)
                    try:
                        for s in stmt.body:
                            self.execute(s)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            return  # éviter de re-boucler ensuite

        # --- SPIRAL : parcours hélicoïdal d'une matrice ---
        if kind == "spiral":
            matrix = [list(row) for row in self.evaluate(stmt.iterator)]
            n_rows = len(matrix)
            n_cols = len(matrix[0]) if n_rows else 0
            total = n_rows * n_cols
            if total == 0:
                return

            mods = stmt.modifiers or {}
            origin = "center"
            direction = "clockwise"
            if "from" in mods:
                origin = mods["from"].get("origin", "center")
                direction = mods["from"].get("direction", "clockwise")

            if origin == "top_left":
                start_r, start_c = 0, 0
            else:
                start_r, start_c = n_rows // 2, n_cols // 2

            if direction == "counterclockwise":
                dirs = [(0, 1), (-1, 0), (0, -1), (1, 0)]   # droite, haut, gauche, bas
            else:
                dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]   # droite, bas, gauche, haut

            visited = set()
            order = []
            r, c = start_r, start_c
            if 0 <= r < n_rows and 0 <= c < n_cols:
                order.append((r, c))
                visited.add((r, c))

            leg = 1
            dir_idx = 0
            safety = 0
            max_leg = n_rows + n_cols + 2
            while len(order) < total and safety < 10000:
                safety += 1
                for _ in range(2):
                    dr, dc = dirs[dir_idx % 4]
                    for _ in range(leg):
                        r += dr
                        c += dc
                        if 0 <= r < n_rows and 0 <= c < n_cols and (r, c) not in visited:
                            order.append((r, c))
                            visited.add((r, c))
                            if len(order) >= total:
                                break
                    dir_idx += 1
                    if len(order) >= total:
                        break
                leg += 1
                if leg > max_leg:
                    break

            for (rr, cc) in order:
                if isinstance(stmt.var_name, tuple):
                    self.env.define(stmt.var_name[0], rr)
                    self.env.define(stmt.var_name[1], cc)
                else:
                    self.env.define(stmt.var_name, matrix[rr][cc])
                try:
                    for s in stmt.body:
                        self.execute(s)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return

        # --- WAVE : parcours oscillatoire (zig-zag) ---
        if kind == "wave":
            mods = stmt.modifiers or {}

            if "amplitude" in mods:
                # liste plate traitée comme une matrice implicite de largeur 'amplitude'
                flat = list(self.evaluate(stmt.iterator))
                width = int(self.evaluate(mods["amplitude"]))
                if width <= 0:
                    width = len(flat) or 1
                chunks = [flat[i:i + width] for i in range(0, len(flat), width)]
                for idx, chunk in enumerate(chunks):
                    seq = chunk if idx % 2 == 0 else list(reversed(chunk))
                    for item in seq:
                        self.env.define(stmt.var_name, item)
                        try:
                            for s in stmt.body:
                                self.execute(s)
                        except BreakException:
                            return
                        except ContinueException:
                            continue
                return

            matrix = [list(row) for row in self.evaluate(stmt.iterator)]
            axis = mods.get("by", "row")

            if axis == "column":
                n_cols = len(matrix[0]) if matrix else 0
                for ci in range(n_cols):
                    col = [matrix[ri][ci] for ri in range(len(matrix))]
                    seq = col if ci % 2 == 0 else list(reversed(col))
                    self.env.define(stmt.var_name, OktopiosList(seq))
                    try:
                        for s in stmt.body:
                            self.execute(s)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            else:
                for ri, row in enumerate(matrix):
                    seq = row if ri % 2 == 0 else list(reversed(row))
                    self.env.define(stmt.var_name, OktopiosList(seq))
                    try:
                        for s in stmt.body:
                            self.execute(s)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
            return

        # --- SECTORS : découpage radial, optionnellement parallèle ---
        if kind == "sectors":
            mods = stmt.modifiers or {}

            if "rows" in mods and "cols" in mods:
                matrix = [list(row) for row in self.evaluate(stmt.iterator)]
                n_rows = len(matrix)
                n_cols = len(matrix[0]) if n_rows else 0
                block_rows = max(1, int(self.evaluate(mods["rows"])))
                block_cols = max(1, int(self.evaluate(mods["cols"])))
                row_size = max(1, -(-n_rows // block_rows))
                col_size = max(1, -(-n_cols // block_cols))
                sectors_list = []
                for br in range(0, n_rows, row_size):
                    for bc in range(0, n_cols, col_size):
                        zone = [OktopiosList(r[bc:bc + col_size]) for r in matrix[br:br + row_size]]
                        sectors_list.append(OktopiosList(zone))
            else:
                items = list(self.evaluate(stmt.iterator))
                count = max(1, int(self.evaluate(mods["count"]))) if "count" in mods else 1
                n = len(items)
                size = max(1, -(-n // count)) if n else 1
                sectors_list = [OktopiosList(items[i:i + size]) for i in range(0, n, size)]

            if not mods.get("parallel"):
                for sector in sectors_list:
                    self.env.define(stmt.var_name, sector)
                    try:
                        for s in stmt.body:
                            self.execute(s)
                    except BreakException:
                        break
                    except ContinueException:
                        continue
                return

            # --- parallel : chaque secteur sur un thread distinct ---
            # self.env est désormais PAR THREAD (voir plus haut dans ce fichier),
            # donc chaque secteur peut s'exécuter en vrai parallèle sans piétiner
            # les autres — exactement "une tentacule par secteur".
            def run_sector(sector_value):
                local_env = Environment(enclosing=self.global_env)
                prev = self.env
                self.env = local_env
                try:
                    self.env.define(stmt.var_name, sector_value)
                    for s in stmt.body:
                        self.execute(s)
                except (BreakException, ContinueException):
                    pass
                finally:
                    self.env = prev

            with ThreadPoolExecutor(max_workers=min(8, len(sectors_list) or 1)) as pool:
                futures = [pool.submit(run_sector, sector) for sector in sectors_list]
                for f in futures:
                    f.result()
            return

        # --- BOUCLE STANDARD ---
        for item in iterable:
            self.env.define(stmt.var_name, item)
            try:
                for s in stmt.body:
                    #print("debug s = ",s)
                    self.execute(s)
            except BreakException:
                break
            except ContinueException:
                continue

    def eval_in_context(self, expr, local_vars):
        """
        Évalue une expression dans un contexte temporaire (comme dans une boucle filtrée ou triée).
        local_vars est un dict {nom_variable: valeur} injecté dans l'environnement temporairement.
        """
        # Sauvegarde de l'environnement actuel
        saved_env = self.env

        # Création d’un environnement local temporaire
        temp_env = Environment(enclosing=saved_env)
        for name, value in local_vars.items():
            temp_env.define(name, value)

        # Remplace temporairement l'environnement courant
        self.env = temp_env
        result = self.evaluate(expr)

        #print("debug : eval_in_context = ", result)

        # Restauration
        self.env = saved_env
        return result

    def eval_condition(self, expr, local_vars):
        """
        Évalue une condition (ex: where (x % 2 == 0)) dans un contexte local.
        Renvoie True/False.
        """
        value = self.eval_in_context(expr, local_vars)
        return bool(value)

    def load_module(self, module_name, alias):
        #print(f"[Module chargé] {module_name}, alias = {alias}")
        if module_name not in self.modules_loaded:
            self.modules_loaded.append(module_name)
            self.modules_loaded_alias[module_name] = alias

    def parse_inline_expression(self, expr_text: str):
        lexer = tokenize(expr_text)
        parser = Parser(lexer)
        for i in self.modules_loaded:
            parser.modules_loaded.add(i)
        for al in self.modules_loaded_alias:
            parser.modules_alias.add(self.modules_loaded_alias[al])
        expr = parser.expression()
        return expr

    #def visit_FuncDecl(self, node):
    #    func = UserFunction(node, self.env)
    #    # Si on est au niveau global → enregistrer dans l'environnement global
    #    if self.env.is_global_scope():
    #        #print(Fore.YELLOW + f"[GLOBAL FUNC REGISTER] {node.name}" + Style.RESET_ALL)
    #        self.global_env.define(node.name, func)
    #    else:
    #        #print(Fore.CYAN + f"[LOCAL FUNC REGISTER] {node.name}" + Style.RESET_ALL)
    #        self.env.define(node.name, func)

    def get_type_name(self, val):
        from . native_collections import ListInstance, TupleInstance, MapInstance, SetInstance
        from . matrix import Matrix
        from . native_advanced_collections import (
            LinkedListInstance,
            TreeSetInstance,
            LinkedHashSetInstance,
            TreeMapInstance,
            MatrixObject
        )
        if val is None: return "void"
        if isinstance(val, bool): return "bool"  # Changé de bool à "bool"
        if isinstance(val, int): return "int"  # Changé d'int à "int"
        if isinstance(val, float): return "float"
        if isinstance(val, str): return "string"
        if isinstance(val, (UserFunction, LambdaFunction)): return "fun"
        if isinstance(val, Matrix): return "Matrix"
        if isinstance(val, MatrixObject): return "Matrix"
        if isinstance(val, LinkedListInstance): return "LinkedList"
        if isinstance(val, TreeSetInstance): return "TreeSet"
        if isinstance(val, LinkedHashSetInstance): return "LinkedHashSet"
        if isinstance(val, TreeMapInstance): return "TreeMap"
        if isinstance(val, ListInstance): return "list"
        if isinstance(val, SetInstance): return "set"
        if isinstance(val, (MapInstance or dict)): return "map"
        if isinstance(val, TupleInstance): return "tuple"
        return val

    def evaluate_in_expr_context(self, expr):
        #print("ici dans evaluate in expr context ", expr)
        old = self.in_expr_context
        self.in_expr_context = True
        result = self.evaluate(expr)
        #print("ici dans evaluate in expr context 2", result)
        self.in_expr_context = old
        return result

    def is_callable(self, obj):
        return isinstance(obj, (UserFunction, LambdaFunction)) or callable(obj)

    def evaluate_binary_op(self, expr):
        left = self.evaluate_in_expr_context(expr.left)
        right = self.evaluate_in_expr_context(expr.right)

        if expr.operator == TokenType.NOT_LIKE or expr.operator == TokenType.NOT_IN :
            op_type = expr.operator
        else:
            op_type = expr.operator.type

        #print("debug : evaluate_binary_op = ", op_type, TokenType.IS_LIKE)

        if op_type == TokenType.GT:
            return left > right
        elif op_type == TokenType.LT:
            return left < right
        elif op_type == TokenType.GE:
            return left >= right
        elif op_type == TokenType.LE:
            return left <= right
        elif op_type == TokenType.EQEQ:
            return left == right
        elif op_type == TokenType.NE:
            return left != right
        elif op_type == TokenType.IN:
            return left in right
        elif op_type == TokenType.NOT_IN:
            return left not in right
        elif op_type == TokenType.IS:
            return left == right
        elif op_type == TokenType.IS_LIKE:
            return str(right) in str(left)
        elif op_type == TokenType.NOT_LIKE:
            return str(right) not in str(left)
        elif op_type == TokenType.OR:
            if isinstance(right, (list, tuple, set, dict, OktopiosList)):
                return left in right
            return self.is_truthy(left) or self.is_truthy(right)
        elif op_type == TokenType.PLUS:
            if isinstance(left, str) and not isinstance(right, str):
                return left + str(right)
            elif not isinstance(left, str) and isinstance(right, str):
                return str(left) + right
            return left + right
        elif op_type == TokenType.MINUS:
            return left - right
        elif op_type == TokenType.STAR:
            result = left * right
            #print("debug : result = ", result)
            return result
        elif op_type == TokenType.PERCENT:
            return left % right
        elif op_type == TokenType.SLASH:
            right = self.evaluate(expr.right)
            if right == 0:
                raise RuntimeError(Fore.CYAN + "Division par zéro"+ Style.RESET_ALL)
            return self.evaluate(expr.left) / right
        else:
            raise Exception(Fore.CYAN + f"[Erreur] Opérateur non supporté : {expr.operator}"+ Style.RESET_ALL)

    def is_truthy(self, value):
        #Null / None
        if value is None:
            return False
        #Bool natif
        if isinstance(value, bool):
            return value
        #Numériques
        if isinstance(value, (int, float)):
            return value != 0
        #String
        if isinstance(value, str):
            return value != ""
        #Liste/Dict/Tuple/ Set
        if isinstance(value, (list, dict, tuple, set)):
            return len(value) > 0

        return True

    def visit_IsEmptyExpr(self, expr):
        value = self.evaluate(expr.expr)

        if value is None:
            return not expr.negate

        try:
            size = len(value)
        except TypeError:
            raise RuntimeError("Type is not iterable and cannot be checked for emptiness.")

        if expr.negate:
            return size != 0
        return size == 0

    def visit_MatchesExpr(self, expr):
        value = str(self.evaluate(expr.expr))
        pattern = str(self.evaluate(expr.pattern))

        return re.match(pattern, value) is not None

    def visit_MatchExpr(self, expr):
        match_value = self.evaluate(expr.value)
        results = []

        for case in expr.cases:
            for pattern in case.patterns:
                if self.match_pattern(match_value, pattern):
                    results.append(self.evaluate(case.body))
                    break

        if not results:
            return self.evaluate(expr.else_branch)
        if len(results) == 1:
            return results[0]
        return OktopiosList(results)

    def match_pattern(self, value, pattern):
        # Pattern avec valeur simple
        if isinstance(pattern, ValuePattern):
            pattern_value = self.evaluate(pattern.expr)
            return value == pattern_value

        # Pattern IN (value in container)
        elif isinstance(pattern, InPattern):
            container = self.evaluate(pattern.pattern)
            return value in container

        # Pattern LIKE: collection membership, otherwise text containment.
        elif isinstance(pattern, LikePattern):
            expected = self.evaluate(pattern.pattern)
            if isinstance(expected, (list, tuple, set, dict, OktopiosList)):
                return value in expected
            return str(expected) in str(value)

        # Pattern BETWEEN
        elif isinstance(pattern, BetweenPattern):
            lower = self.evaluate(pattern.lower)
            upper = self.evaluate(pattern.upper)
            return lower <= value <= upper

        # Pattern MATCHES (regex)
        elif isinstance(pattern, RegexPattern):
            regex_str = str(self.evaluate(pattern.pattern_expr))
            return re.match(regex_str, str(value)) is not None

        # Pattern IS TYPE
        elif isinstance(pattern, TypePattern):
            type_token = pattern.type_token
            type_map = {
                TokenType.INT: int,
                TokenType.STRING: str,
                TokenType.FLOAT: float,
                TokenType.BOOL: bool,
            }
            expected_type = type_map.get(type_token.type)
            return isinstance(value, expected_type)

        # Pattern RANGE (X|Y)
        elif isinstance(pattern, RangePattern):
            start = self.evaluate(pattern.start)
            end = self.evaluate(pattern.end)
            return start <= value <= end

        # Fallback: évaluation directe
        else:
            pattern_value = self.evaluate(pattern)
            return value == pattern_value

    # ------------------------------------------------------------------
    # neuron_loop / __matches_db__  (mémoire associative "Elementor")
    # ------------------------------------------------------------------
    def visit_NeuronLoopDecl(self, decl):
        db = NeuronLoopDB(decl.name)
        for neuro_block in decl.neurons:
            db.add_neuron(self.build_neuron_runtime(neuro_block))
        db.build_index()  # index (champ, valeur) -> emplacements, construit une seule fois
        with self._shared_lock:
            self.matches_db[decl.name] = db
        self.env.define(decl.name, db)
        return None

    def build_neuron_runtime(self, neuro_block):
        enter = {cat: self.evaluate(expr) for cat, expr in neuro_block.enter.items()}
        out_blocks = {
            out_name: {
                "ports": {cat: self.evaluate(expr) for cat, expr in block["ports"].items()},
                "target": block["target"],
            }
            for out_name, block in neuro_block.out_blocks.items()
        }
        memory = self.build_category_section(neuro_block.memory)
        elementor = self.build_category_section(neuro_block.elementor)
        return NeuroRuntime(neuro_block.name, enter, memory, elementor, out_blocks)

    def build_category_section(self, categories):
        result = {}
        for category, entries in categories.items():
            store = CategoryStore()
            for ref_name, entry in entries.items():
                store.place(ref_name, self.build_ref_entry(entry))
            result[category] = store
        return result

    def build_ref_entry(self, entry):
        id_value = self.evaluate(entry.id_expr)
        data = {}
        for key_expr, value_node in entry.data_pairs:
            key_value = self.evaluate(key_expr)
            if isinstance(value_node, RefValue):
                data[key_value] = RefMarker(value_node.name)
            else:
                data[key_value] = self.evaluate(value_node)
        return RefEntryRuntime(entry.name, id_value, data)

    def _find_matches(self, db, value, motif, threshold_count):
        """ÉTAPE COMMUNE À TOUTE REQUÊTE __matches_db__, quel que soit le verbe
        (select / insert / update / delete / reflexion) : la correspondance.
        C'est le principe biologique de base — un cerveau qui reçoit une
        information commence TOUJOURS par essayer de la reconnaître avant
        d'agir dessus (mémoriser, corriger, oublier, ou simplement se
        rappeler). Aucun verbe ne contourne cette étape.

        Renvoie une liste de (neuro_name, section, categorie, ref_name, entry, count)."""
        candidate_locations = db.candidates_for_value(value)
        if candidate_locations:
            candidates = {loc: self._location_entry(db, loc) for loc in candidate_locations}
        else:
            candidates = {(n, s, c, r): e for n, s, c, r, e in db.all_locations()}

        matches = []
        for (neuro_name, section, category, ref_name), entry in candidates.items():
            count = self.count_motif_matches(db, neuro_name, entry, motif)
            if count >= threshold_count:
                matches.append((neuro_name, section, category, ref_name, entry, count))
        return matches

    def visit_MatchesDbExpr(self, expr):
        value = self.evaluate(expr.value)
        db = self.matches_db.get(expr.db_name)
        if db is None:
            raise Exception(
                f"[Erreur] Base __matches_db__ inconnue : '{expr.db_name}' "
                f"(aucune déclaration 'neuron_loop {expr.db_name}' trouvée)."
            )

        # Verrou PROPRE À CETTE BASE (pas un verrou global) : deux tentacules
        # qui interrogent des bases __matches_db__ DIFFÉRENTES restent donc
        # vraiment parallèles ; seules les requêtes sur LA MÊME base sont
        # sérialisées entre elles (lecture comme écriture), ce qui évite
        # toute corruption de l'index ou des structures internes.
        with db.lock:
            verb = getattr(expr, "verb", None) or "select"

            # Axon Hillock : seuil de déclenchement.
            # - select/insert/update/delete (défaut) : TOUTES les conditions du motif.
            # - reflexion (défaut) : associatif/exploratoire, un seul indice suffit
            #   à amorcer la pensée — comme une réminiscence partielle.
            if expr.threshold is not None:
                threshold_count = self.evaluate(expr.threshold)
            elif verb == "reflexion":
                threshold_count = 1 if expr.motif else 0
            else:
                threshold_count = len(expr.motif)

            # --- LA correspondance, commune à tous les verbes ---
            matches = self._find_matches(db, value, expr.motif, threshold_count)

            if verb == "delete":
                return self._verb_delete(db, matches)
            if verb == "update":
                return self._verb_update(db, matches, expr.set_clause)
            if verb == "reflexion":
                return self._verb_reflexion(db, matches, expr.motif, threshold_count)

            # --- select / insert (insert = select qui autocrée si rien ne répond) ---
            results = []
            for neuro_name, section, category, ref_name, entry, count in matches:
                # Schwann Cell : le signal se propage le long de l'axone vers le(s)
                # neurone(s) connecté(s) via 'target', tant que ceux-ci répondent
                # eux aussi au même motif/seuil (sinon la propagation s'arrête là).
                propagation = self.propagate(db, neuro_name, expr.motif, threshold_count)
                results.append(self._entry_to_okp(
                    neuro_name, section, category, ref_name, entry,
                    fired=True, matched_criteria=count, threshold=threshold_count,
                    propagation=propagation,
                ))

            # Aucune correspondance : on crée un nouveau neurone/élément si
            # 'autocreate <categorie>' (ou 'insert <categorie>') a été demandé,
            # en respectant les limites Elementor (7 x 8 x 7000).
            if not results and expr.autocreate:
                data = self._motif_to_data(expr.motif, value)
                try:
                    neuro_name, ref_name, entry, neuron_created = db.create_element(expr.autocreate, data)
                except CapacityFullError as e:
                    raise Exception(f"[Erreur] __matches_db__ autocreate '{expr.db_name}.{expr.autocreate}' : {e}")

                results.append(self._entry_to_okp(
                    neuro_name, "elementor", expr.autocreate, ref_name, entry,
                    fired=True, matched_criteria=0, threshold=threshold_count,
                    propagation=[neuro_name], created=True, neuron_created=neuron_created,
                ))

            return OktopiosList(results)

    def _verb_delete(self, db, matches):
        """DELETE : la correspondance détermine QUOI supprimer — rien n'est
        jamais supprimé sans avoir d'abord été reconnu."""
        deleted = []
        for neuro_name, section, category, ref_name, entry, count in matches:
            neuro = db.neurons[neuro_name]
            section_map = neuro.memory if section == "memory" else neuro.elementor
            store = section_map.get(category)
            if store is not None:
                store.remove(ref_name)
            # Désindexation incrémentale (O(champs de l'entrée), jamais un
            # rebuild complet — important sur une grosse base).
            db.unindex_entry(neuro_name, section, category, ref_name, entry)
            deleted.append(self._entry_to_okp(
                neuro_name, section, category, ref_name, entry,
                fired=True, matched_criteria=count, threshold=None, propagation=[neuro_name],
            ))
        return OktopiosList(deleted)

    def _verb_update(self, db, matches, set_clause):
        """UPDATE : la correspondance détermine QUOI modifier ; 'set {...}'
        indique les nouvelles valeurs à appliquer sur chaque entrée trouvée."""
        if not set_clause:
            raise Exception("[Erreur] __matches_db__ update nécessite une clause 'set { ... }'")
        new_values = {self.evaluate(k): self.evaluate(v) for k, v in set_clause}

        updated = []
        for neuro_name, section, category, ref_name, entry, count in matches:
            # Désindexe l'ANCIEN état, applique les nouvelles valeurs, puis
            # réindexe le NOUVEL état — incrémental, jamais un rebuild complet.
            db.unindex_entry(neuro_name, section, category, ref_name, entry)
            entry.data.update(new_values)
            db.index_entry(neuro_name, section, category, ref_name, entry)
            updated.append(self._entry_to_okp(
                neuro_name, section, category, ref_name, entry,
                fired=True, matched_criteria=count, threshold=None, propagation=[neuro_name],
            ))
        return OktopiosList(updated)

    def _verb_reflexion(self, db, matches, motif, threshold_count):
        """REFLEXION : exploration purement associative, AUCUNE mutation.
        Met en avant la chaîne de propagation (ce à quoi la pensée 'mène')
        plutôt que la simple liste des entrées correspondantes."""
        thoughts = []
        seen_chains = set()
        for neuro_name, section, category, ref_name, entry, count in matches:
            propagation = self.propagate(db, neuro_name, motif, threshold_count)
            chain_key = tuple(propagation)
            if chain_key in seen_chains:
                continue
            seen_chains.add(chain_key)
            thoughts.append(self._entry_to_okp(
                neuro_name, section, category, ref_name, entry,
                fired=True, matched_criteria=count, threshold=threshold_count,
                propagation=propagation,
            ))
        return OktopiosList(thoughts)

    def _motif_to_data(self, motif, value):
        """Construit les données d'un nouvel élément à partir du motif :
        chaque champ avec une valeur concrète (ValuePattern) est repris tel
        quel ; les autres (is/between/like/=>...) ne peuvent pas être
        traduits en valeur concrète et sont laissés vides ([])."""
        data = {}
        for field_expr, pattern in motif:
            field_name = self.evaluate(field_expr)
            if isinstance(pattern, ValuePattern):
                data[field_name] = self.evaluate(pattern.expr)
            else:
                data[field_name] = []
        return data

    def _location_entry(self, db, loc):
        neuro_name, section, category, ref_name = loc
        neuro = db.neurons[neuro_name]
        section_map = neuro.memory if section == "memory" else neuro.elementor
        return section_map[category][ref_name]

    def count_motif_matches(self, db, neuro_name, entry, motif):
        """Nombre de critères du motif satisfaits par cette entrée (utilisé
        à la fois pour le filtrage et pour le seuil de déclenchement)."""
        count = 0
        for field_expr, pattern in motif:
            field_name = self.evaluate(field_expr)
            field_value = entry.data.get(field_name)
            if self.match_db_pattern(db, neuro_name, field_value, pattern):
                count += 1
        return count

    def neuron_fires(self, db, neuro_name, motif, threshold_count):
        """Vrai si AU MOINS une entrée de ce neurone (memory ou elementor)
        atteint le seuil pour ce motif — sert à la propagation synaptique."""
        neuro = db.neurons.get(neuro_name)
        if neuro is None:
            return False
        for section in (neuro.memory, neuro.elementor):
            for entries in section.values():
                for entry in entries.values():
                    if self.count_motif_matches(db, neuro_name, entry, motif) >= threshold_count:
                        return True
        return False

    def propagate(self, db, start_neuro_name, motif, threshold_count, _visited=None):
        """Chemin de propagation du signal : neurone de départ, puis chaque
        neurone cible (via out_X.target) qui répond encore au même motif,
        de proche en proche — comme un potentiel d'action qui sautille de
        nœud de Ranvier en nœud de Ranvier jusqu'au prochain neurone."""
        visited = _visited if _visited is not None else set()
        if start_neuro_name in visited:
            return []
        visited.add(start_neuro_name)

        chain = [start_neuro_name]
        neuro = db.neurons.get(start_neuro_name)
        if neuro is None:
            return chain

        for _out_name, target in neuro.synapse_targets():
            if target in visited or target not in db.neurons:
                continue
            if self.neuron_fires(db, target, motif, threshold_count):
                chain.extend(self.propagate(db, target, motif, threshold_count, visited))
                break  # un seul chemin de propagation actif à la fois

        return chain

    def _entry_to_okp(self, neuro_name, section, category, ref_name, entry,
                       fired=None, matched_criteria=None, threshold=None, propagation=None,
                       created=None, neuron_created=None):
        payload = {
            "neuron": neuro_name,
            "section": section,
            "category": category,
            "ref": ref_name,
            "id": entry.id,
            "data": OktopiosMap(entry.to_okp_dict()),
        }
        if fired is not None:
            payload["fired"] = fired
            payload["matched_criteria"] = matched_criteria
            payload["threshold"] = threshold
            payload["propagation"] = OktopiosList(propagation or [])
        if created is not None:
            payload["created"] = created
            payload["neuron_created"] = bool(neuron_created)
        return OktopiosMap(payload)

    def match_db_pattern(self, db, neuro_name, field_value, pattern):
        # `=> nom` dans le motif : vrai si le champ EST une référence vers `nom`.
        if isinstance(pattern, DbRefPattern):
            return isinstance(field_value, RefMarker) and field_value.name == pattern.name

        # Sinon, une référence non résolue est comparée via sa cible résolue.
        if isinstance(field_value, RefMarker):
            resolved = db.resolve_marker(neuro_name, field_value)
            field_value = resolved.to_okp_dict() if resolved else None

        try:
            return self.match_pattern(field_value, pattern)
        except Exception:
            return False

    def visit_IsTypeExpr(self, expr):
        value = self.evaluate(expr.expr)

        type_map = {
            TokenType.INT: int,
            TokenType.STRING: str,
            TokenType.FLOAT: float,
            TokenType.BOOL: bool,
        }

        expected_type = type_map.get(expr.type_token.type)

        return isinstance(value, expected_type)

    def visit_BetweenExpr(self, expr):
        value = self.evaluate(expr.expr)
        lower = self.evaluate(expr.lower)
        upper = self.evaluate(expr.upper)

        return lower <= value <= upper

    def evaluate_func_call(self, func_call):
        name = func_call.name
        args = [self.evaluate(arg) for arg in func_call.arguments]
        # 🔹 Fonctions natives
        if name in self.native_construct:
            try:
                return self.native_construct[name](*args)
            except Exception as e:
                raise Exception(
                    Fore.CYAN + f"[Erreur lors de l'appel de la fonction native '{name}']: {str(e)}" + Style.RESET_ALL)

        arity = len(args)

        # 🔥 Déterminer les types des arguments
        arg_types = [self.get_type_name(arg) for arg in args]
        type_signature = ",".join(arg_types)

        # 🔥 Chercher avec signature complète d'abord
        full_key = f"{name}/{arity}/{type_signature}"
        func = self.env.get(full_key, suppress_errors=True)
        if func is NOT_FOUND:
            func = None

        # 🔥 Sinon, chercher seulement par arité (compatible avec conversion implicite ?)
        if func is None:
            # Chercher toutes les fonctions avec cette arité
            candidates = []
            for key, value in self.env.values.items():
                if key.startswith(f"{name}/{arity}/"):
                    # Parsing de la signature attendue
                    expected_types = key.split("/")[2].split(",")
                    # Vérifier compatibilité des types
                    compatible = True
                    for i, expected in enumerate(expected_types):
                        if expected == "int" and arg_types[i] == "float":
                            # Conversion int ← float possible (troncature)
                            pass
                        elif expected == "float" and arg_types[i] == "int":
                            # Conversion float ← int possible
                            pass
                        elif expected != arg_types[i]:
                            compatible = False
                            break
                    if compatible:
                        candidates.append((key, value))

            if candidates:
                # Prendre la première compatible (ou gérer l'ambiguïté)
                func = candidates[0][1]


        # 🔹 Sinon, essayer sans arité (pour les fonctions avec valeur par défaut)
        if func is None:
            func = self.env.get(name, suppress_errors=True)
            if func is NOT_FOUND:
                func = None

        # ✅ Vérifier l'arité du fallback, en tenant compte des paramètres à
        # valeur par défaut (le code ci-dessus dit explicitement que ce
        # fallback sert "pour les fonctions avec valeur par défaut", mais la
        # vérification exigeait une arité EXACTE et bloquait donc justement
        # ce cas — bug trouvé via la suite de tests).
        if func is not None and isinstance(func, UserFunction) and func.declaration is not None:
            params = func.declaration.params
            expected_arity = len(params)
            min_required = sum(1 for p in params if p[3] is None)
            if len(args) < min_required or len(args) > expected_arity:
                if min_required == expected_arity:
                    raise Exception(
                        f"[Erreur] La fonction '{name}' attend {expected_arity} argument(s), "
                        f"mais {len(args)} ont été fournis."
                    )
                raise Exception(
                    f"[Erreur] La fonction '{name}' attend entre {min_required} et {expected_arity} "
                    f"argument(s), mais {len(args)} ont été fournis."
                )


        # 🔹 Sinon, essayer une variable contenant une fonction
        if func is None:
            value = self.env.get(name, arity=None, suppress_errors=True)
            if value is NOT_FOUND:
                value = None
            if self.is_callable(value):
                func = value

        # 🔹 Si une fonction valide est trouvée, on l'appelle
        if func:
            if self.is_callable(func):
                if isinstance(func, UserFunction):
                    if getattr(func.declaration, "return_type", None) == "void" and self.in_expr_context:
                        raise Exception(
                            Fore.CYAN + f"[Erreur] La fonction '{name}' est void et ne peut pas être utilisée dans une expression" + Style.RESET_ALL)

                    valeurReturn = func.call(self, args)

                    # --- Logique de vérification ---
                    actual_return_type = self.get_type_name(valeurReturn)
                    declared_return_type = func.declaration.return_type

                    # Vérification TOUJOURS active
                    if declared_return_type != actual_return_type:
                        # Cas spécial : une fonction qui retourne une autre fonction
                        if declared_return_type == "fun" and self.is_callable(valeurReturn):
                            # OK, une fonction peut retourner une fonction
                            pass
                        elif declared_return_type == None:
                            # les fonctions sans type de retour explicite sont vérifiées comme si elles retournaient None
                            pass
                        else:
                            raise Exception(
                                Fore.CYAN + "[" + Style.RESET_ALL +
                                Fore.LIGHTYELLOW_EX + "Erreur" + Style.RESET_ALL +
                                Fore.CYAN + "] La fonction" + Style.RESET_ALL +
                                Fore.LIGHTWHITE_EX + f" '{name}' " + Style.RESET_ALL +
                                Fore.CYAN + f" est déclarée comme retournant " + Style.RESET_ALL +
                                Fore.LIGHTWHITE_EX + f"[{declared_return_type}]" + Style.RESET_ALL +
                                Fore.CYAN + " mais a retourné du type " + Style.RESET_ALL +
                                Fore.LIGHTYELLOW_EX + f"[{actual_return_type}]" + Style.RESET_ALL
                            )

                    return valeurReturn

                if isinstance(func, LambdaFunction):
                    return func.call(self, args)

                return func(*args)

            raise Exception(Fore.CYAN + f"[Erreur] '{name}' n'est pas une fonction." + Style.RESET_ALL)

        raise Exception(Fore.CYAN + f"[Erreur] Fonction inconnue : {name}" + Style.RESET_ALL)

    def evaluate_func_inject_call(self, func_call):
        name = func_call.func
        module = func_call.module
        args = [self.evaluate(arg) for arg in func_call.arguments]

        # Résolution inverse : si module est un alias, retrouver le nom réel
        resolved_module = module
        for alias, real_name in self.modules_loaded_alias.items():
            if real_name == module:
                resolved_module = alias
                break

        # Vérifie si le module (ou son alias) est injecté
        is_injected = resolved_module in self.modules_loaded and resolved_module in self.native_funcs

        if is_injected:
            try:
                return self.native_funcs[resolved_module][name](*args)
            except Exception as e:
                raise Exception(
                    Fore.CYAN + f"[Erreur lors de l'appel de la fonction native '{resolved_module}.{name}']: {str(e)}" + Style.RESET_ALL
                )

        # Vérifie si c’est un module importé (.okp)
        elif module in self.module_cache:
            module_interp = self.module_cache[module]
            #print("module_interp", module_interp)
            func = module_interp.env.get(name)
            #print("func", func)

            if func is None:
                raise Exception(
                    Fore.CYAN + f"[Erreur] Fonction '{name}' introuvable dans le module '{module}'" + Style.RESET_ALL)

            # Appel direct de la fonction du module importé
            return func.call(self, args, func_call.line, func_call.column)

        else:
            raise Exception(Fore.CYAN + f"[Erreur] Module '{module}' non injecté ni importé" + Style.RESET_ALL)

    def visit_UpadateDictLiteral(self, expr):
        result = {}
        from . native_collections import NativeCollectionsFuncs as NCF
        target = self.env.get(expr.target.name)  # ✅ récupère la vraie map
        for key_expr, val_expr in expr.updates.pairs:
            key = self.evaluate(key_expr)
            val = self.evaluate(val_expr)
            result[key] = val
            NCF["mapUpdate"](target, {key: val})  # ✅ objet MapInstance réel

        return result

    def methode_func_call(self, func_call):
        #name = func_call.name
        args = [self.evaluate(arg) for arg in func_call.arguments]
        return args[0]

    def execute_block(self, statements, environment):
        previous = self.env
        try:
            self.env = environment
            for statement in statements:
                #print(previous)
                self.execute(statement)
        finally:
            self.env = previous

    #def visit_GetExpr(self, expr):
    #    obj = self.evaluate(expr.obj)
    #    if isinstance(obj, RuntimeInstance):
    #        field = obj.get_field(expr.name, current_class=self.current_class)
    #        return field.value
    #    raise Exception(f"[Erreur] Impossible d'accéder au champ {expr.name}")

    #def visit_SetExpr(self, expr):
    #    obj = self.evaluate(expr.obj)  # évalue "p"
    #    value = self.evaluate(expr.value)  # évalue "Soule"
    #    if isinstance(obj, RuntimeInstance):
    #        obj.set_field(expr.name, value, current_class=self.current_class)
    #        return value
    #    raise Exception(f"[Erreur] Impossible d’assigner le champ {expr.name}")

    def resolve_module_path(self, module_name):
        """
        Convertit un nom de module 'a.b.c' en chemin de fichier et cherche dans
        les module_search_paths. Retourne le chemin si trouvé, sinon None.
        """
        candidate_rel = module_name.replace(".", "/") + ".okp"
        for root in self.module_search_paths:
            path = os.path.join(root, candidate_rel)
            if os.path.isfile(path):
                return path
            # aussi accepter module_name.okp au niveau racine du root
            path2 = os.path.join(root, module_name + ".okp")
            if os.path.isfile(path2):
                return path2
        return None

    def check_name_conflict(self, name):
        """Vérifie qu’un symbole ou alias n’est pas déjà défini dans l’environnement global."""
        if self.env.exists(name):
            raise Exception(
                f"[Conflit de nom] Le symbole ou alias '{name}' est déjà défini dans l'environnement global.")
        if name in self.env.imported_modules:
            raise Exception(f"[Conflit d'import] L'alias '{name}' est déjà utilisé pour un module importé.")

    def import_module(self, module_name, alias=None, force_reload=False):
        # Vérif de conflit d’alias
        if alias:
            self.check_name_conflict(alias)

        # Vérif de conflit d’alias
        if alias and alias in self.env.imported_modules:
            raise Exception(f"[Conflit d'importation] L'alias '{alias}' est déjà utilisé pour un autre module.")

        # Charger le module (même logique qu’avant)
        module_interp = self.module_cache.get(module_name)
        if module_interp is None or force_reload:
            path = self.resolve_module_path(module_name)
            if path is None:
                raise Exception(f"[Import] Module '{module_name}' introuvable.")
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()

            tokens = list(tokenize(code))
            parser = Parser(tokens)
            ast = parser.parse()

            module_interp = Interpreter()
            module_interp.module_name = module_name

            module_interp.interpret(ast)
            self.module_cache[module_name] = module_interp

        proxy = ModuleProxy(module_interp, module_name, alias)
        self.env.import_module(module_name, alias, proxy)
        return proxy

    def from_import(self, module_name, names):
        module_interp = self.module_cache.get(module_name)
        if module_interp is None:
            module_interp = self.import_module(module_name)

        env = getattr(module_interp, "env", None)
        if env is None:
            raise Exception(f"[from . import] Module '{module_name}' sans environnement valide.")

        if names == ["*"]:
            # Importation globale sans vérif (option : avertir)
            candidates = []
            for field in ("values", "store", "_values", "symbols"):
                if hasattr(env, field):
                    d = getattr(env, field)
                    if isinstance(d, dict):
                        candidates = list(d.items())
                        break
            for k, v in candidates:
                if self.env.exists(k):
                    print(f"[Avertissement] Redéfinition du symbole global '{k}' via 'from . {module_name} import *'")
                self.env.define(k, v)
            return

        # Importation sélective
        for entry in names:
            if isinstance(entry, tuple):
                name, alias = entry
            else:
                name, alias = entry, None

            alias_name = alias or name

            # Vérif de conflit
            self.check_name_conflict(alias_name)

            # Recherche du symbole
            val = None
            if hasattr(env, "get"):
                val = env.get(name, suppress_errors=True)
                if val is NOT_FOUND:
                    val = None
            if val is None:
                for field in ("values", "store", "_values", "symbols"):
                    if hasattr(env, field):
                        d = getattr(env, field)
                        if not isinstance(d, dict):
                            continue
                        if name in d:
                            val = d[name]
                            break
                        for key, v in d.items():
                            if key.startswith(f"{name}/"):
                                val = v
                                break
                        if val is not None:
                            break
            if val is None:
                raise Exception(f"[from . import] Symbole '{name}' introuvable dans '{module_name}'")

            # Définir le symbole dans l’environnement
            self.env.define(alias_name, val)

    def use_file(self, path_literal):
        """
        use "file.okp" : exécute le contenu du fichier dans l'env courant.
        path_literal : la valeur string (chemin), relatif possible.
        """
        path = path_literal
        # si chemin relatif, normaliser par rapport au CWD
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.isfile(path):
            raise Exception(f"[use] Fichier {path} introuvable")
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        tokens = list(tokenize(code))
        parser = Parser(tokens)
        ast = parser.parse()
        # Exécuter dans l'env courant (attention: expose defs au scope courant)
        self.interpret(ast)

    def visit_ImportStmt(self, stmt):
        proxy = self.import_module(module_name=stmt.module)
        for name in stmt.names:
            if name == "*":
                env = getattr(proxy._module_interp, "env", None)
                if env and hasattr(env, "values"):
                    for sym_name, value in env.values.items():
                        # Nettoyage du nom si arité (ex: "foo/2" → "foo")
                        clean_name = sym_name.split("/")[0]
                        self.env.define(clean_name, value)
            elif isinstance(name, tuple):
                original, alias = name
                alias_name = alias or original

                # 🔍 Vérification de conflit d’alias
                self.check_name_conflict(alias_name)

                if original == stmt.module:
                    self.env.import_module(original, alias, proxy)
                    self.env.define(alias_name, proxy)
                    if alias is not None:
                        self.module_cache[alias] = proxy._module_interp
                    continue
                value = proxy.get(original)
                self.env.define(alias_name, value)
            else:
                # import simple sans alias
                self.check_name_conflict(name)
                value = proxy.get(name)
                self.env.define(name, value)

        return None

        #return self.import_module(stmt.module, alias=stmt.alias)

    def visit_FromImportStmt(self, stmt):
        self.from_import(stmt.module, stmt.names)
        return None

    def visit_UseStmt(self, stmt):
        # stmt.path est une string déjà tokenisée dans l'AST
        self.use_file(stmt.path)
        return None

    def visit_Delete(self, stmt):
        var_name = stmt.name

        # Vérifie si la variable existe
        value = self.env.get(var_name)
        if value is None:
            raise Exception(f"[Erreur] Variable '{var_name}' introuvable pour suppression")

        # Si c’est une instance d’objet
        if isinstance(value, RuntimeInstance):
            destructor = value.fieldsMeth.get("__destruct")
            if destructor:
                if isinstance(destructor, UserFunction):
                    destructor.call(interpreter=self, args=None)
                elif callable(destructor):
                    destructor()

        # Supprime la variable de l’environnement
        self.env.values.pop(var_name, None)
        #print(f"[OK] Objet '{var_name}' détruit proprement.")



class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

