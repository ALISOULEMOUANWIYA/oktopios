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
}

