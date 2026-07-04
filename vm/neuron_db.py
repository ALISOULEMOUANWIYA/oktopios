"""
neuron_db.py
------------
Représentation runtime des bases déclarées avec `neuron_loop` et interrogées
avec l'opérateur `__matches_db__`.

Modèle (inspiré du schéma "Elementor" : alpha/beta/gamma/ohm/dzêta) :

    NeuronLoopDB
      └── neurons: { neuro_name -> NeuroRuntime }
                NeuroRuntime
                  ├── enter:   { categorie -> adresse }
                  ├── memory:  { categorie -> { ref_name -> RefEntryRuntime } }
                  ├── elementor: { categorie -> { ref_name -> RefEntryRuntime } }
                  └── out_blocks: { out_name -> { categorie -> adresse } }
                            RefEntryRuntime
                              ├── id
                              └── data: { champ -> valeur | RefMarker }

Un champ peut contenir soit une valeur concrète (texte, nombre, liste...),
soit un RefMarker("beta_2") qui signifie "ce champ est une référence
croisée vers le canal/entrée beta_2" (issu de la notation `=> beta_2`).

Pour la performance, un index plat {(champ, valeur) -> [emplacements]} est
construit une seule fois à la déclaration, afin que __matches_db__ n'ait
jamais besoin de re-scanner toute la base à chaque appel.
"""


class CapacityFullError(Exception):
    """Levée quand une catégorie a atteint sa limite Elementor
    (7 divisions x 8 sous-divisions x 7000 éléments) dans UN neurone donné —
    signal qu'il faut créer un nouveau neurone pour accueillir l'élément."""
    pass


class CategoryStore(dict):
    """Stockage d'une catégorie (alpha/beta/gamma/ohm/dzêta).

    Se comporte comme un dict {ref_name: RefEntryRuntime} (100% rétro-
    compatible avec le reste du code), tout en assignant chaque entrée à une
    division (1..7) / sous-division (1..8) — limites du modèle Elementor :
    chaque sous-division est plafonnée à 7000 éléments.
    """

    MAX_DIVISIONS = 7
    MAX_SUBDIVISIONS = 8
    MAX_PER_SUBDIVISION = 7000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._slots = {}    # ref_name -> (division, subdivision)
        self._counts = {}   # (division, subdivision) -> nombre d'éléments

    def place(self, ref_name, entry):
        """Place une entrée dans le premier slot disponible (en respectant
        l'ordre division puis sous-division). Lève CapacityFullError si la
        catégorie est saturée dans ce neurone."""
        for d in range(1, self.MAX_DIVISIONS + 1):
            for s in range(1, self.MAX_SUBDIVISIONS + 1):
                count = self._counts.get((d, s), 0)
                if count < self.MAX_PER_SUBDIVISION:
                    self[ref_name] = entry
                    self._slots[ref_name] = (d, s)
                    self._counts[(d, s)] = count + 1
                    return d, s
        raise CapacityFullError(
            "Catégorie saturée : 7 divisions x 8 sous-divisions x 7000 éléments atteints"
        )

    def slot_of(self, ref_name):
        return self._slots.get(ref_name)

    def has_room(self):
        return any(
            self._counts.get((d, s), 0) < self.MAX_PER_SUBDIVISION
            for d in range(1, self.MAX_DIVISIONS + 1)
            for s in range(1, self.MAX_SUBDIVISIONS + 1)
        )

    def remove(self, ref_name):
        """Retire une entrée et libère sa place (utilisé par le verbe delete)."""
        if ref_name not in self:
            return False
        del self[ref_name]
        slot = self._slots.pop(ref_name, None)
        if slot is not None:
            self._counts[slot] = max(0, self._counts.get(slot, 1) - 1)
        return True


class RefMarker:
    """Représente une valeur `=> nom` non résolue : une référence croisée
    vers une autre porte/entrée nommée `nom` (ex: 'beta_2', 'ohm_4')."""
    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, RefMarker) and self.name == other.name

    def __hash__(self):
        return hash(("RefMarker", self.name))

    def __repr__(self):
        return f"=> {self.name}"


class RefEntryRuntime:
    __slots__ = ("name", "id", "data")

    def __init__(self, name, id_value, data):
        self.name = name
        self.id = id_value
        self.data = data  # dict champ -> valeur | RefMarker

    def to_okp_dict(self):
        """Représentation exposée côté langage Oktopios (sans les RefMarker bruts)."""
        out = {}
        for k, v in self.data.items():
            out[k] = (f"=> {v.name}" if isinstance(v, RefMarker) else v)
        return out


class NeuroRuntime:
    __slots__ = ("name", "enter", "memory", "elementor", "out_blocks")

    def __init__(self, name, enter, memory, elementor, out_blocks):
        self.name = name
        self.enter = enter
        self.memory = memory
        self.elementor = elementor
        self.out_blocks = out_blocks

    def find_ref(self, ref_name):
        """Cherche une entrée (memory ou elementor) par son nom déclaré,
        peu importe la catégorie."""
        for section in (self.memory, self.elementor):
            for category, entries in section.items():
                if ref_name in entries:
                    return category, entries[ref_name]
        return None, None

    def category_for_alias(self, alias):
        """Résout un alias type 'beta_2' -> nom de catégorie 'beta',
        en se basant sur les adresses déclarées dans enter{}/out_X{}."""
        for cat in self.enter:
            if alias == f"{cat}_{self.enter[cat]}":
                return cat
        for out_block in self.out_blocks.values():
            for cat in out_block["ports"]:
                if alias == f"{cat}_{out_block['ports'][cat]}":
                    return cat
        # fallback : préfixe avant le premier underscore
        prefix = alias.split("_")[0]
        return prefix if prefix in self.enter else None

    def synapse_targets(self):
        """Liste des neurones cibles déclarés via 'target:' dans les blocs
        out_X (la "Schwann Cell" : axon terminal -> dendrite du neurone suivant)."""
        targets = []
        for out_name, out_block in self.out_blocks.items():
            if out_block.get("target"):
                targets.append((out_name, out_block["target"]))
        return targets


class NeuronLoopDB:
    """Une base déclarée par `neuron_loop NomDB { ... }`."""

    def __init__(self, name):
        self.name = name
        self.neurons = {}     # neuro_name -> NeuroRuntime
        self._index = {}      # (champ, valeur) -> [(neuro, section, categorie, ref_name)]
        self._auto_counter = 0
        import threading
        self.lock = threading.RLock()  # une base = un verrou ; deux bases différentes restent parallèles

    # ------------------------------------------------------------------
    # construction
    # ------------------------------------------------------------------
    def add_neuron(self, neuro_runtime):
        self.neurons[neuro_runtime.name] = neuro_runtime

    def build_index(self):
        """Construit l'index plat (champ, valeur) -> emplacements pour que
        __matches_db__ n'ait jamais à scanner toute la base. Appelé une
        seule fois, à la déclaration."""
        self._index.clear()
        for neuro_name, neuro in self.neurons.items():
            for section_name, section in (("memory", neuro.memory), ("elementor", neuro.elementor)):
                for category, entries in section.items():
                    for ref_name, entry in entries.items():
                        self.index_entry(neuro_name, section_name, category, ref_name, entry)

    def index_entry(self, neuro_name, section_name, category, ref_name, entry):
        """Ajoute UNE entrée à l'index sans tout reconstruire — utilisé à la
        fois par build_index() et par la création automatique d'éléments."""
        for field, value in entry.data.items():
            if isinstance(value, RefMarker):
                continue  # indexé via DbRefPattern, pas via égalité
            if isinstance(value, (list, dict)):
                continue  # listes/dicts vides ou complexes : pas indexables simplement
            key = (field, value)
            self._index.setdefault(key, []).append(
                (neuro_name, section_name, category, ref_name)
            )

    def unindex_entry(self, neuro_name, section_name, category, ref_name, entry):
        """Retire UNE entrée de l'index sans tout reconstruire — utilisé par
        delete/update pour rester rapide même sur une grosse base (on ne
        rebuild plus l'index complet à chaque appel)."""
        loc = (neuro_name, section_name, category, ref_name)
        for field, value in entry.data.items():
            if isinstance(value, RefMarker) or isinstance(value, (list, dict)):
                continue
            key = (field, value)
            locations = self._index.get(key)
            if locations and loc in locations:
                locations.remove(loc)
                if not locations:
                    del self._index[key]

    # ------------------------------------------------------------------
    # interrogation
    # ------------------------------------------------------------------
    def all_locations(self):
        """Toutes les entrées de la base, sous forme de tuples
        (neuro_name, section, categorie, ref_name, entry)."""
        for neuro_name, neuro in self.neurons.items():
            for section_name, section in (("memory", neuro.memory), ("elementor", neuro.elementor)):
                for category, entries in section.items():
                    for ref_name, entry in entries.items():
                        yield neuro_name, section_name, category, ref_name, entry

    def candidates_for_value(self, value):
        """Utilise l'index pour ne renvoyer que les entrées qui ont AU MOINS
        un champ égal à `value` (ou contenant `value` si chaîne) — sert de
        filtre rapide avant d'appliquer le motif complet."""
        seen = set()
        result = []
        for (field, indexed_value), locations in self._index.items():
            match = (indexed_value == value)
            if not match and isinstance(indexed_value, str) and isinstance(value, str):
                match = value in indexed_value
            if match:
                for loc in locations:
                    if loc not in seen:
                        seen.add(loc)
                        result.append(loc)
        return result

    # ------------------------------------------------------------------
    # création automatique (aucune correspondance trouvée)
    # ------------------------------------------------------------------
    def _neuron_with_room(self, category):
        """Premier neurone existant dont la catégorie a encore de la place
        en elementor (7 divisions x 8 sous-divisions x 7000 éléments)."""
        for neuro_name, neuro in self.neurons.items():
            store = neuro.elementor.get(category)
            if store is None or store.has_room():
                return neuro_name
        return None

    def create_element(self, category, data, ref_name=None):
        """Crée un nouvel élément dans `category`, en réutilisant un neurone
        existant qui a encore de la place ; si AUCUN n'a de place (limites
        Elementor atteintes partout), un nouveau neurone est créé pour
        l'accueillir. Renvoie (neuro_name, ref_name, entry, neuron_created)."""
        neuro_name = self._neuron_with_room(category)
        neuron_created = False

        if neuro_name is None:
            self._auto_counter += 1
            neuro_name = f"neuro_auto_{self._auto_counter}"
            neuro = NeuroRuntime(neuro_name, enter={}, memory={}, elementor={}, out_blocks={})
            self.add_neuron(neuro)
            neuron_created = True

        neuro = self.neurons[neuro_name]
        if category not in neuro.elementor:
            neuro.elementor[category] = CategoryStore()
        store = neuro.elementor[category]

        if ref_name is None:
            self._auto_counter += 1
            ref_name = f"auto_{self._auto_counter}"
        id_value = self._auto_counter

        entry = RefEntryRuntime(ref_name, id_value, data)
        store.place(ref_name, entry)  # peut lever CapacityFullError si la course est perdue
        self.index_entry(neuro_name, "elementor", category, ref_name, entry)

        return neuro_name, ref_name, entry, neuron_created

    def resolve_marker(self, neuro_name, marker):
        """Résout un RefMarker('beta_2') dans le contexte d'un neurone donné :
        renvoie l'entrée (memory/elementor) de la catégorie correspondante,
        ou None si non résolvable."""
        neuro = self.neurons.get(neuro_name)
        if neuro is None:
            return None
        category = neuro.category_for_alias(marker.name)
        if category is None:
            return None
        for section in (neuro.elementor, neuro.memory):
            entries = section.get(category, {})
            if entries:
                # priorité : entrée dont l'id correspond au suffixe numérique de l'alias, sinon la première
                suffix = marker.name.rsplit("_", 1)[-1]
                for entry in entries.values():
                    if str(entry.id) == suffix:
                        return entry
                return next(iter(entries.values()))
        return None

    # ------------------------------------------------------------------
    # persistance disque (sauvegarde/restauration JSON)
    # ------------------------------------------------------------------
    def to_dict(self):
        """Sérialise toute la base (structure + données) en dict JSON-able."""
        def section_to_dict(section):
            return {
                category: {
                    ref_name: {
                        "id": entry.id,
                        "data": {
                            k: ({"__ref__": v.name} if isinstance(v, RefMarker) else v)
                            for k, v in entry.data.items()
                        },
                    }
                    for ref_name, entry in entries.items()
                }
                for category, entries in section.items()
            }

        return {
            "name": self.name,
            "auto_counter": self._auto_counter,
            "neurons": {
                neuro_name: {
                    "enter": dict(neuro.enter),
                    "memory": section_to_dict(neuro.memory),
                    "elementor": section_to_dict(neuro.elementor),
                    "out_blocks": {
                        out_name: {"ports": dict(block["ports"]), "target": block.get("target")}
                        for out_name, block in neuro.out_blocks.items()
                    },
                }
                for neuro_name, neuro in self.neurons.items()
            },
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruit une base à partir du dict produit par to_dict()."""
        db = cls(data["name"])
        db._auto_counter = data.get("auto_counter", 0)

        def section_from_dict(section_data):
            section = {}
            for category, entries in section_data.items():
                store = CategoryStore()
                for ref_name, entry_data in entries.items():
                    raw_data = {}
                    for k, v in entry_data["data"].items():
                        if isinstance(v, dict) and "__ref__" in v:
                            raw_data[k] = RefMarker(v["__ref__"])
                        else:
                            raw_data[k] = v
                    store.place(ref_name, RefEntryRuntime(ref_name, entry_data["id"], raw_data))
                section[category] = store
            return section

        for neuro_name, neuro_data in data["neurons"].items():
            neuro = NeuroRuntime(
                neuro_name,
                enter=dict(neuro_data.get("enter", {})),
                memory=section_from_dict(neuro_data.get("memory", {})),
                elementor=section_from_dict(neuro_data.get("elementor", {})),
                out_blocks={
                    out_name: {"ports": dict(block.get("ports", {})), "target": block.get("target")}
                    for out_name, block in neuro_data.get("out_blocks", {}).items()
                },
            )
            db.add_neuron(neuro)

        db.build_index()
        return db

    def save(self, path):
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return True

    @classmethod
    def load(cls, path):
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
