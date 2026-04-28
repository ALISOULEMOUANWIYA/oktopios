# =====================================================
# native_advanced_funcs.py
# =====================================================

from .native_advanced_collections import *
from .matrix import Matrix

# =====================================================
# --- Fonctions natives pour Oktopios (collections avancées) ---
# =====================================================
NativeAdvancedFuncs = {
    # --- LinkedList ---
    "LinkedList":{
        "llAdd": lambda ll, v: ll.add(v),
        "llAddAll": lambda ll, vals: [ll.add(v) for v in vals],
        "llRemove": lambda ll, v: ll.remove(v),
        "llRemoveAll": lambda ll, vals: [ll.remove(v) for v in vals],
        "llList": lambda ll: ll.to_list(),
    },

    # --- TreeSet ---
    "TreeSet":{
        "tsAdd": lambda ts, v: ts.add(v),
        "tsAddAll": lambda ts, vals: [ts.add(v) for v in vals],
        "tsRemove": lambda ts, v: ts.remove(v),
        "tsRemoveAll": lambda ts, vals: [ts.remove(v) for v in vals],
        "tsHas": lambda ts, v: ts.contains(v),
        "tsList": lambda ts: ts.to_list(),
    },

    # --- LinkedHashSet ---
    "LinkedHashSet":{
        "lhsAdd": lambda lhs, v: lhs.add(v),
        "lhsList": lambda lhs: lhs.to_list(),
        "lhsHas": lambda lhs, v: lhs.contains(v),
        "lhsRemove": lambda lhs, v: lhs.remove(v),
        "lhsAddAll": lambda lhs, vals: [lhs.add(v) for v in vals],
        "lhsRemoveAll": lambda lhs, vals: [lhs.remove(v) for v in vals],
    },

    # --- TreeMap ---
    "TreeMap":{
        "tmPut": lambda tm, k, v: tm.put(k, v),
        "tmPutAll": lambda tm, d: [tm.put(k, v) for k, v in d.items()],
        "tmGet": lambda tm, k: tm.get(k),
        "tmRemove": lambda tm, k: tm.remove(k),
        "tmRemoveAll": lambda tm, keys: [tm.remove(k) for k in keys],
        "tmKeys": lambda tm: tm.keys(),
        "tmVals": lambda tm: tm.values_list(),
    },

    # --- Utils ---
    "check":{
        "swap": lambda lst, i, j: swap(lst, i, j),
        "rev": lambda lst: reverseOrder(lst),
        "search": lambda lst, val: binarySearch(lst, val),
    },

    # --- Iterator ---
    "Iterator":{
        "itHas": lambda it: it.hasNext(),
        "itNext": lambda it: it.next(),
    },
    # --- Matrix ---
    "Matrix": {
        "set": lambda m, coords, val: m.set(coords, val),
        "get": lambda m, coords: m.get(coords),
        "link": lambda m, coordsA, other, coordsB, meta=None, directed=False: m.link(coordsA, other, coordsB, meta, directed),
        "traverse": lambda m, coords, strategy="dfs": m.traverse(coords, strategy),
        "detect_cycle": lambda m, coords: m.detect_cycle(coords),
        "add": lambda A, B: Matrix.add(A, B),
        "tensor": lambda A, B: Matrix.tensor(A, B),
        "contract": lambda A, B, dA, dB: Matrix.contract(A, B, dA, dB),
    },
}


