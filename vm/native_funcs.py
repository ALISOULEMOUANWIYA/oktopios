# Implémentation inline de camelCase (évite la dépendance externe)
class CamelCase:
    def hump(self, s: str) -> str:
        """Convertit 'hello world' en 'helloWorld'."""
        words = s.replace("-", " ").replace("_", " ").split()
        if not words:
            return s
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])
import time as _time
import os
import sys
import random as _random
import math
import platform
import shutil, subprocess, ctypes
try:
    import psutil as _psutil
except ImportError:
    _psutil = None
import json as _json
import sqlite3 as _sqlite3
import difflib as _difflib
from . ast_nodes import OktopiosMap as _OktopiosMap, OktopiosList as _OktopiosList
try:
    import openpyxl as _openpyxl
except ImportError:
    _openpyxl = None
try:
    import requests as _requests
except ImportError:
    _requests = None
try:
    import pymysql as _pymysql
except ImportError:
    _pymysql = None
try:
    import cv2 as _cv2
except ImportError:
    _cv2 = None
try:
    import numpy as _np
    import librosa as _librosa
except ImportError:
    _np = None
    _librosa = None


# ---------------------------------------------------------------------------
# Reconnaissance faciale (détection + empreinte par histogramme de niveaux
# de gris, comparable via corrélation) — classique/hors-ligne, sans dlib.
# ---------------------------------------------------------------------------

_FACE_CASCADE = None


def _get_face_cascade():
    global _FACE_CASCADE
    if _FACE_CASCADE is None:
        cascade_path = _cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        _FACE_CASCADE = _cv2.CascadeClassifier(cascade_path)
    return _FACE_CASCADE


def _facial_extract(path):
    if _cv2 is None:
        raise ImportError("opencv n'est pas installé. Lancez : pip install opencv-contrib-python-headless")
    img = _cv2.imread(path)
    if img is None:
        raise ValueError(f"Image illisible : {path}")
    gray = _cv2.cvtColor(img, _cv2.COLOR_BGR2GRAY)
    faces = _get_face_cascade().detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))

    results = []
    for (x, y, w, h) in faces:
        face = _cv2.resize(gray[y:y + h, x:x + w], (100, 100))
        hist = _cv2.calcHist([face], [0], None, [256], [0, 256])
        _cv2.normalize(hist, hist)
        results.append(_OktopiosMap({
            "box": _OktopiosList([int(x), int(y), int(w), int(h)]),
            "fingerprint": _OktopiosList([float(v) for v in hist.flatten()]),
        }))
    return _OktopiosList(results)


def _facial_similarity(fp1, fp2):
    if _cv2 is None or _np is None:
        raise ImportError("opencv n'est pas installé. Lancez : pip install opencv-contrib-python-headless")
    a = _np.array(list(fp1), dtype="float32")
    b = _np.array(list(fp2), dtype="float32")
    return float(_cv2.compareHist(a, b, _cv2.HISTCMP_CORREL))


# ---------------------------------------------------------------------------
# Reconnaissance vocale (empreinte MFCC moyenne, comparable par similarité
# cosinus) — classique/hors-ligne, sans moteur de transcription.
# ---------------------------------------------------------------------------

def _vocal_extract(path, n_mfcc=20):
    if _librosa is None:
        raise ImportError("librosa n'est pas installé. Lancez : pip install librosa soundfile")
    y, sr = _librosa.load(path, sr=None, mono=True)
    mfcc = _librosa.feature.mfcc(y=y, sr=sr, n_mfcc=int(n_mfcc))
    fingerprint = _np.mean(mfcc, axis=1)
    return _OktopiosList([float(v) for v in fingerprint])


def _vocal_similarity(fp1, fp2):
    if _np is None:
        raise ImportError("librosa/numpy non installés. Lancez : pip install librosa soundfile")
    a = _np.array(list(fp1), dtype="float64")
    b = _np.array(list(fp2), dtype="float64")
    denom = _np.linalg.norm(a) * _np.linalg.norm(b)
    return float(_np.dot(a, b) / denom) if denom else 0.0


# ---------------------------------------------------------------------------
# Connecteurs de données (json / excel / sql / mysql) — pour __matches_db__
# Les résultats sont enveloppés en OktopiosMap/OktopiosList pour s'intégrer
# nativement au reste du langage (boucles for-in, .get(), affichage, etc.)
# ---------------------------------------------------------------------------

def _wrap_rows(rows):
    return _OktopiosList([_OktopiosMap(dict(r)) for r in rows])


def _read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = _json.load(f)
    if isinstance(data, list):
        return _wrap_rows(data) if data and isinstance(data[0], dict) else _OktopiosList(data)
    if isinstance(data, dict):
        return _OktopiosMap(data)
    return data


def _read_excel(path, sheet=0):
    if _openpyxl is None:
        raise ImportError("openpyxl n'est pas installé. Lancez : pip install openpyxl")
    wb = _openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[sheet] if isinstance(sheet, int) else wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return _OktopiosList([])
    headers = [str(h) if h is not None else f"col{i}" for i, h in enumerate(rows[0])]
    return _wrap_rows(dict(zip(headers, row)) for row in rows[1:])


def _read_sql(path, query="SELECT name FROM sqlite_master WHERE type='table'"):
    """Lit une base SQLite (.db/.sqlite) ou exécute un script .sql (chargé
    dans une base en mémoire) puis lance `query` et renvoie les lignes."""
    if str(path).lower().endswith(".sql"):
        conn = _sqlite3.connect(":memory:")
        with open(path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
    else:
        conn = _sqlite3.connect(path)
    conn.row_factory = _sqlite3.Row
    rows = [dict(row) for row in conn.execute(query).fetchall()]
    conn.close()
    return _wrap_rows(rows)


def _read_mysql(host, user, password, database, query, port=3306):
    if _pymysql is None:
        raise ImportError("pymysql n'est pas installé. Lancez : pip install pymysql")
    conn = _pymysql.connect(
        host=host, user=user, password=password, database=database,
        port=int(port), cursorclass=_pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(query)
            return _wrap_rows(cur.fetchall())
    finally:
        conn.close()


def _unwrap(value):
    """Convertit OktopiosMap/OktopiosList (récursivement) en dict/list Python
    natifs, pour pouvoir les sérialiser (json/excel/sql/mysql)."""
    if isinstance(value, _OktopiosMap):
        entries = value.entries if value.entries is not None else dict(value)
        return {k: _unwrap(v) for k, v in entries.items()}
    if isinstance(value, _OktopiosList):
        elements = value.elements if value.elements is not None else list(value)
        return [_unwrap(v) for v in elements]
    if isinstance(value, dict):
        return {k: _unwrap(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_unwrap(v) for v in value]
    return value


def _as_rows(data):
    rows = _unwrap(data)
    if isinstance(rows, dict):
        rows = [rows]
    return rows or []


def _write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        _json.dump(_unwrap(data), f, ensure_ascii=False, indent=2)
    return True


def _write_excel(path, data, sheet_name="Sheet1"):
    if _openpyxl is None:
        raise ImportError("openpyxl n'est pas installé. Lancez : pip install openpyxl")
    rows = _as_rows(data)
    wb = _openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([row.get(h) for h in headers])
    wb.save(path)
    return True


def _write_sql(path, table, data):
    rows = _as_rows(data)
    if not rows:
        return False
    columns = list(rows[0].keys())
    conn = _sqlite3.connect(path)
    col_defs = ", ".join(f'"{c}"' for c in columns)
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
    placeholders = ", ".join("?" for _ in columns)
    for row in rows:
        conn.execute(
            f'INSERT INTO "{table}" ({col_defs}) VALUES ({placeholders})',
            [row.get(c) for c in columns],
        )
    conn.commit()
    conn.close()
    return True


def _sql_type_for(value):
    if isinstance(value, bool):
        return "BOOLEAN"
    if isinstance(value, int):
        return "BIGINT"
    if isinstance(value, float):
        return "DOUBLE"
    return "TEXT"


def _write_mysql(host, user, password, database, table, data, port=3306):
    if _pymysql is None:
        raise ImportError("pymysql n'est pas installé. Lancez : pip install pymysql")
    rows = _as_rows(data)
    if not rows:
        return False
    columns = list(rows[0].keys())
    conn = _pymysql.connect(host=host, user=user, password=password, database=database, port=int(port))
    try:
        with conn.cursor() as cur:
            # Crée la table si elle n'existe pas encore (contrairement à SQLite,
            # MySQL ne le fait jamais implicitement — bug trouvé en testant
            # contre un vrai serveur MariaDB).
            col_defs_create = ", ".join(
                f"`{c}` {_sql_type_for(rows[0][c])}" for c in columns
            )
            cur.execute(f"CREATE TABLE IF NOT EXISTS `{table}` ({col_defs_create})")

            col_list = ", ".join(f"`{c}`" for c in columns)
            placeholders = ", ".join(["%s"] * len(columns))
            cur.executemany(
                f"INSERT INTO `{table}` ({col_list}) VALUES ({placeholders})",
                [tuple(row.get(c) for c in columns) for row in rows],
            )
        conn.commit()
        return True
    finally:
        conn.close()


def _text_normalize(s):
    return str(s).strip().lower()


def _text_similarity(a, b):
    return _difflib.SequenceMatcher(None, _text_normalize(a), _text_normalize(b)).ratio()


# ---------------------------------------------------------------------------
# IA Adaptive Module (Heart 3) — Ollama (local) / DeepSeek / StarCoder
# ---------------------------------------------------------------------------

def _retry_call(fn, retries=2, backoff=1.0):
    """Réessaie fn() en cas d'échec TRANSITOIRE (connexion, timeout, 5xx),
    jamais sur une erreur permanente (401/403/404) — inutile de réessayer
    une clé API invalide. Backoff exponentiel entre les tentatives."""
    import time as _t
    last_exc = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            msg = str(e)
            permanent = any(code in msg for code in (" 401", " 403", " 404", "Unauthorized", "Forbidden"))
            if permanent or attempt == retries:
                raise
            _t.sleep(backoff * (2 ** attempt))
    raise last_exc


def _require_requests():
    if _requests is None:
        raise ImportError(
            "Le module Python 'requests' n'est pas installé. "
            "Lancez : pip install requests (nécessaire pour IAModule.*)"
        )
    return _requests


def _ia_ollama(prompt, model="llama3", host="http://localhost:11434", timeout=60, retries=2):
    """Appelle un serveur Ollama LOCAL (à lancer côté Ali : `ollama serve`).
    CodeLlama et Mistral n'ont pas besoin d'une fonction séparée : ce sont
    juste des modèles Ollama, ex. model='codellama' ou model='mistral'
    (après `ollama pull codellama` / `ollama pull mistral`).
    Aucune restriction réseau ici puisque c'est du localhost, mais ça
    nécessite que le serveur tourne réellement sur la machine qui exécute
    le programme Oktopios."""
    requests = _require_requests()

    def _do():
        resp = requests.post(
            f"{host}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")

    try:
        return _retry_call(_do, retries=retries)
    except Exception as e:
        raise Exception(f"[IAModule.ollama] Impossible de contacter Ollama sur {host} (modèle '{model}') après {retries + 1} tentative(s) : {e}")


def _ia_ollama_stream(prompt, model, host, timeout, on_chunk):
    """Variante streaming : appelle on_chunk(texte_partiel) à chaque morceau
    reçu d'Ollama, et renvoie le texte complet accumulé à la fin. Garde la
    connexion "vivante" sur les génrations longues plutôt qu'une seule
    attente bloquante."""
    requests = _require_requests()
    import json as _json
    full_text = []
    with requests.post(
        f"{host}/api/generate",
        json={"model": model, "prompt": prompt, "stream": True},
        timeout=timeout,
        stream=True,
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = _json.loads(line)
            piece = chunk.get("response", "")
            if piece:
                full_text.append(piece)
                if on_chunk is not None:
                    on_chunk(piece)
            if chunk.get("done"):
                break
    return "".join(full_text)


def _ia_deepseek(prompt, api_key=None, model=None, timeout=60, retries=2, host="http://localhost:11434"):
    """DeepSeek est open source (licence MIT pour R1) et disponible
    directement via Ollama — donc PAR DÉFAUT (pas de api_key fournie), on
    route vers Ollama local, gratuit, sans clé : `ollama pull deepseek-r1`.
    Si une api_key EST fournie, on utilise l'API hébergée payante à la place
    (utile si la machine ne peut pas faire tourner le modèle localement)."""
    if not api_key:
        return _ia_ollama(prompt, model or "deepseek-r1", host, timeout, retries)

    requests = _require_requests()

    def _do():
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"model": model or "deepseek-chat", "messages": [{"role": "user", "content": prompt}]},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    try:
        return _retry_call(_do, retries=retries)
    except Exception as e:
        raise Exception(f"[IAModule.deepseek] Erreur API DeepSeek après {retries + 1} tentative(s) : {e}")


def _ia_starcoder(prompt, api_key=None, model=None, timeout=60, retries=2, host="http://localhost:11434"):
    """StarCoder2 est open source (licence BigCode OpenRAIL-M) et disponible
    directement via Ollama — donc PAR DÉFAUT (pas de api_key fournie), on
    route vers Ollama local, gratuit, sans clé : `ollama pull starcoder2`.
    Si une api_key EST fournie, on utilise l'API d'inférence Hugging Face
    à la place (utile si la machine ne peut pas faire tourner le modèle
    localement — vérifier que le modèle visé est encore dispo en serverless)."""
    if not api_key:
        return _ia_ollama(prompt, model or "starcoder2", host, timeout, retries)

    requests = _require_requests()

    def _do():
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model or 'bigcode/starcoder2-15b'}",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"inputs": prompt},
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0].get("generated_text", "")
        return str(data)

    try:
        return _retry_call(_do, retries=retries)
    except Exception as e:
        raise Exception(f"[IAModule.starcoder] Erreur API StarCoder après {retries + 1} tentative(s) : {e}")




NativeFuncs = {
    "Math" : {
        # --- Maths de base ---
        "abs": lambda x: abs(x),
        "round": lambda x, n=0: round(x, int(n)),
        "floor": lambda x: math.floor(x),
        "ceil": lambda x: math.ceil(x),
        "sqrt": lambda x: math.sqrt(x),
        "pow": lambda x, y: math.pow(x, y),
        "max": lambda *args: max(args),
        "min": lambda *args: min(args),
        # --- Maths avancées ---
        "factorial": lambda x: math.factorial(int(x)),
        "log": lambda x: math.log(x),
        "log10": lambda x: math.log10(x),
        "exp": lambda x: math.exp(x),
        "sin": lambda x: math.sin(x),
        "cos": lambda x: math.cos(x),
        "tan": lambda x: math.tan(x),
        "asin": lambda x: math.asin(x),
        "acos": lambda x: math.acos(x),
        "atan": lambda x: math.atan(x),
        "deg": lambda x: math.degrees(x),
        "rad": lambda x: math.radians(x),
    },
    "Time":{
        # --- Temps ---
        "sleep": lambda s: _time.sleep(float(s)),
        "time": lambda *args: _time.time(),
        "date": lambda *args: _time.strftime("%Y-%m-%d %H:%M:%S"),
        "ctime": lambda *args: _time.ctime(),
    },
    "String":{
        "trim": lambda s: s.strip(),
        "upper": lambda s: s.upper(),
        "lower": lambda s: s.lower(),
        "length": lambda s: len(s),
        "contains": lambda s, sub: sub in s,
        "replace": lambda s, a, b: s.replace(a, b),
        "substring": lambda s, start, end: s[start:end],
        "toString": lambda x: str(x),
        "startswith": lambda s, prefix: s.startswith(prefix),
        "startsWith": lambda s, prefix: s.startswith(prefix),
        "endsWith": lambda s, suffix: s.endswith(suffix),
        "indexof": lambda s, sub: s.find(sub),
        "isempty": lambda s: s == "",
        "camelcase": lambda s: CamelCase().hump(s),
        "compareTo": lambda a, b: (a > b) - (a < b),
        "compare": lambda a, b: (a > b) - (a < b),
        "equals": lambda a, b: a == b,
        "hashCode": lambda x: hash(x),
        "capitalize": lambda s: str(s).capitalize(),
        "reverse": lambda s: str(s)[::-1],
        "split": lambda s, sep=" ": s.split(sep),
    },
    "File":{
        # --- Fichiers & répertoires ---
        "mkdir": lambda path: os.makedirs(path, exist_ok=True),
        "rmdir": lambda path: os.rmdir(path),
        "remove": lambda path: os.remove(path),
        "rename": lambda src, dst: os.rename(src, dst),
        "exists": lambda path: os.path.exists(path),
        "isfile": lambda path: os.path.isfile(path),
        "isdir": lambda path: os.path.isdir(path),
        "read": lambda path: open(path, 'r', encoding='utf-8').read(),
        "readfile": lambda path: open(path, 'r', encoding='utf-8').read(),
        "write": lambda path, content: open(path, 'w', encoding='utf-8').write(content),
        "writefile": lambda path, content: open(path, 'w', encoding='utf-8').write(content),
        "append": lambda path, content: open(path, 'a', encoding='utf-8').write(content),
        "appendfile": lambda path, content: open(path, 'a', encoding='utf-8').write(content),
        "hashfile": lambda path, algo="sha256": __import__('hashlib').new(algo, open(path, 'rb').read()).hexdigest(),
        "zip": lambda src, dst: shutil.make_archive(dst, 'zip', src),
        "unzip": lambda zip_path, extract_to: shutil.unpack_archive(zip_path, extract_to),
        "copy": lambda src, dst: shutil.copy2(src, dst),
        "move": lambda src, dst: shutil.move(src, dst),
        "size": lambda path: os.path.getsize(path),
        "listdir": lambda path=".": os.listdir(path),
        "readlines": lambda path: open(path, 'r', encoding='utf-8').read().splitlines(),
    },
    "Environnement": {
        # --- Environnement ---
        "getenv": lambda var: os.getenv(var),
        "setenv": lambda var, val: os.environ.__setitem__(var, val),
        "delenv": lambda var: os.environ.__delitem__(var) if var in os.environ else None,
        "env": lambda *args: dict(os.environ),
    },
    "Processus": {
        # --- Processus ---
        "pid": lambda *args: os.getpid(),
        "ppid": lambda *args: os.getppid(),
        "run": lambda cmd: os.popen(cmd).read(),
    },
    "Identity": {
        # --- Utilisateur ---
        "user": lambda *args: os.getlogin() if hasattr(os, 'getlogin') else os.getenv("USER") or os.getenv("USERNAME"),
        "home": lambda *args: os.path.expanduser("~"),
        "is_admin": lambda *args: os.getuid() == 0 if hasattr(os, 'getuid') else ctypes.windll.shell32.IsUserAnAdmin() if os.name == 'nt' else False,
        "is_virtual_env": lambda *args: hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix),
        "is_docker": lambda *args: os.path.exists('/.dockerenv'),
        "hostname": lambda *args: platform.node(),
        "platform": lambda *args: platform.platform(),
    },
    "System": {
        # --- Système & environnement ---
        "clear": lambda *args: os.system('cls' if os.name == 'nt' else 'clear'),
        "cls": lambda *args: os.system('cls' if os.name == 'nt' else 'clear'),
        "exit": lambda code=0: sys.exit(int(code)),
        "cwd": lambda *args: os.getcwd(),
        "cd": lambda path: os.chdir(path),
        "ls": lambda path=".": os.listdir(path),
        "sysinfo": lambda *args: {
            "os": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "cwd": os.getcwd()
        },
        "whoami": lambda *args: os.getlogin() if hasattr(os, 'getlogin') else os.getenv("USER") or os.getenv("USERNAME"),
        "uid": lambda *args: os.getuid() if hasattr(os, 'getuid') else None,
        "gid": lambda *args: os.getgid() if hasattr(os, 'getgid') else None,
        "chmod": lambda path, mode: os.chmod(path, int(mode, 8)),
        "chown": lambda path, uid, gid: os.chown(path, uid, gid) if hasattr(os, 'chown') else None,
        "stat": lambda path: os.stat(path),
        "access": lambda path, mode: os.access(path, mode),  # mode = os.R_OK, os.W_OK, os.X_OK
        "uname": lambda *args: platform.uname()._asdict(),
        "cpu_count": lambda *args: os.cpu_count(),
        "loadavg": lambda *args: os.getloadavg() if hasattr(os, 'getloadavg') else None,
        "uptime": lambda *args: _time.time() - _psutil.boot_time() if _psutil else None,
        "disk_usage": lambda path=".": shutil.disk_usage(path)._asdict(),
        "memory_info": lambda *args: _psutil.virtual_memory()._asdict() if _psutil else None,
        "which": lambda cmd: shutil.which(cmd),
        "run": lambda cmd: os.popen(cmd).read(),
        "exec": lambda cmd: subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout,
        #"python_version": lambda *args: platform.python_version(),
    },
    "Random":{
        "random": lambda *args: _random.random(),
        # Nombre aléatoire entier entre min et max inclus
        "randInt": lambda min_val, max_val: _random.randint(int(min_val), int(max_val)),
        # Nombre aléatoire flottant entre min et max
        "randFloat": lambda min_val, max_val: _random.uniform(float(min_val), float(max_val)),
    },
    "Size_STR": {
        "len": lambda x: len(x),
        "length": lambda x: len(x),
    },
    "Type": {
        "type": lambda x: str(type(x).__name__),
    },
    "ValueTO": {
        "ascii": lambda c: ord(str(c)[0]),
        "toChar": lambda n: chr(int(n)),
        "toInt": lambda x: int(x) if x is not None else 0,
        "toFloat": lambda x: float(x) if x is not None else 0.0,
        "toBool": lambda x: bool(x) if x is not None else False,
    },
    "Size_T": {
        "range": lambda a, b=None: list(range(int(a), int(b))) if b is not None else list(range(int(a))),
    },
    "DataImport": {
        # --- Connecteurs de données pour __matches_db__ ---
        "readJson": lambda path: _read_json(path),
        "readExcel": lambda path, sheet=0: _read_excel(path, sheet),
        "readSQL": lambda path, query="SELECT name FROM sqlite_master WHERE type='table'": _read_sql(path, query),
        "readMySQL": lambda host, user, password, database, query, port=3306: _read_mysql(host, user, password, database, query, port),
        "writeJson": lambda path, data: _write_json(path, data),
        "writeExcel": lambda path, data, sheet="Sheet1": _write_excel(path, data, sheet),
        "writeSQL": lambda path, table, data: _write_sql(path, table, data),
        "writeMySQL": lambda host, user, password, database, table, data, port=3306: _write_mysql(host, user, password, database, table, data, port),
    },
    "Recognize": {
        # --- Reconnaissance textuelle ---
        "textNormalize": lambda s: _text_normalize(s),
        "textSimilarity": lambda a, b: _text_similarity(a, b),
        # --- Reconnaissance faciale : détection + empreinte (histogramme), hors-ligne ---
        "facial": lambda path: _facial_extract(path),
        "facialSimilarity": lambda fp1, fp2: _facial_similarity(fp1, fp2),
        # --- Reconnaissance vocale : empreinte MFCC, hors-ligne ---
        "vocal": lambda path, n_mfcc=20: _vocal_extract(path, n_mfcc),
        "vocalSimilarity": lambda fp1, fp2: _vocal_similarity(fp1, fp2),
    },
    "IAModule": {
        # --- Heart 3 / Adaptive Engine : modèles externes ---
        # CodeLlama et Mistral : pas de fonction séparée, juste un modèle
        # Ollama -> ollama(prompt, "codellama") ou ollama(prompt, "mistral")
        # (après 'ollama pull codellama' / 'ollama pull mistral').
        # DeepSeek et StarCoder sont open source et dispo via Ollama : sans
        # api_key, ils tournent en local gratuitement ; avec une api_key,
        # ils utilisent l'API hébergée payante correspondante.
        "ollama": lambda prompt, model="llama3", host="http://localhost:11434", timeout=60, retries=2: _ia_ollama(prompt, model, host, timeout, retries),
        "deepseek": lambda prompt, api_key=None, model=None, timeout=60, retries=2, host="http://localhost:11434": _ia_deepseek(prompt, api_key, model, timeout, retries, host),
        "starcoder": lambda prompt, api_key=None, model=None, timeout=60, retries=2, host="http://localhost:11434": _ia_starcoder(prompt, api_key, model, timeout, retries, host),
    },
}

