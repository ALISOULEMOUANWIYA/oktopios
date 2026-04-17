# native_collections.py
from collections.abc import Iterable

# -------------------------------
# Classes Oktopios
# -------------------------------
class ListInstance:
    def __init__(self, values=None):
        self.values = list(values or [])

    def __str__(self):
        return str(self.values)


class TupleInstance:
    def __init__(self, values=None):
        self.values = tuple(values or [])

    def __str__(self):
        return str(self.values)


class MapInstance:
    def __init__(self, values=None):
        # ✅ Si on reçoit déjà un dict (comme {"A": 10, "B": 20})
        if isinstance(values, dict):
            #print(f"Debug : dists {values}")
            self.values = dict(values)
        # ✅ Si on reçoit une liste de paires [["A", 10], ["B", 20]]
        elif isinstance(values, (list, tuple)):
            #print(f"Debug : listes {values}")
            self.values = dict(values)
        else:
            #print(f"Debug : autre {values}")
            self.values = {}

    def __str__(self):
        return str(self.values)


class SetInstance:
    def __init__(self, values=None):
        self.values = set(values or [])

    def __str__(self):
        return str(self.values)


# -------------------------------
# Fonctions natives
# -------------------------------
NativeCollectionsFuncs = {
    # =====================================================
    # --- List ---
    # =====================================================
    "listAppend":  lambda l, x: l.values.append(x) if isinstance(l, ListInstance) else l.append(x),
    "listExtend":  lambda l, it: l.values.extend(it) if isinstance(l, ListInstance) else l.extend(it),
    "listInsert":  lambda l, i, x: l.values.insert(i, x) if isinstance(l, ListInstance) else l.insert(i, x),
    "listRemove":  lambda l, x: l.values.remove(x) if isinstance(l, ListInstance) else l.remove(x),
    "listPop":     lambda l, i=None: (l.values.pop(i) if i is not None else l.values.pop()) if isinstance(l, ListInstance)
                                    else (l.pop(i) if i is not None else l.pop()),
    "listClear":   lambda l: l.values.clear() if isinstance(l, ListInstance) else l.clear(),
    "listIndex":   lambda l, x: l.values.index(x) if isinstance(l, ListInstance) else l.index(x),
    "listCount":   lambda l, x: l.values.count(x) if isinstance(l, ListInstance) else l.count(x),
    "listSort":    lambda l: l.values.sort() if isinstance(l, ListInstance) else l.sort(),
    "listReverse": lambda l: l.values.reverse() if isinstance(l, ListInstance) else l.reverse(),
    "listCopy":    lambda l: ListInstance(list(l.values)) if isinstance(l, ListInstance) else l.copy(),

    # =====================================================
    # --- Tuple ---
    # =====================================================
    "tupleCount":  lambda t, x: t.values.count(x) if isinstance(t, TupleInstance) else t.count(x),
    "tupleIndex":  lambda t, x: t.values.index(x) if isinstance(t, TupleInstance) else t.index(x),
    "tupleJoin": lambda t, other: (
        TupleInstance(t.values + tuple(other))
        if isinstance(t, TupleInstance)
        else tuple(t) + tuple(other)
    ),

    "tupleRemove": lambda t, other: (
        TupleInstance(tuple(x for x in t.values if x not in other))
        if isinstance(t, TupleInstance)
        else tuple(x for x in t if x not in other)
    ),

    # =====================================================
    # --- Map / Dictionnaire ---
    # =====================================================
    "mapGet":           lambda m, k, default=None: m.values.get(k, default) if isinstance(m, MapInstance) else m.get(k, default),
    "mapKeys":          lambda m: list(m.values.keys()) if isinstance(m, MapInstance) else list(m.keys()),
    "mapValues":        lambda m: list(m.values.values()) if isinstance(m, MapInstance) else list(m.values()),
    "mapItems":         lambda m: list(m.values.items()) if isinstance(m, MapInstance) else list(m.items()),
    "mapSet":           lambda m, k, v: m.values.update({k: v}) if isinstance(m, MapInstance) else m.update({k: v}),
    "mapUpdate":        lambda m, other: m.values.update(other) if isinstance(m, MapInstance) else m.update(other),
    "mapPop":           lambda m, k, default=None: m.values.pop(k, default) if isinstance(m, MapInstance) else m.pop(k, default),
    "mapPopItem":       lambda m: m.values.popitem() if isinstance(m, MapInstance) else m.popitem(),
    "mapClear":         lambda m: m.values.clear() if isinstance(m, MapInstance) else m.clear(),
    "mapSetDefault":    lambda m, k, default=None: m.values.setdefault(k, default) if isinstance(m, MapInstance) else m.setdefault(k, default),
    "mapCopy":          lambda m: MapInstance(dict(m.values)) if isinstance(m, MapInstance) else m.copy(),
    "mapFromKeys":      lambda seq, value=None: MapInstance({k: value for k in seq}),

    # =====================================================
    # --- Set ---
    # =====================================================
    "setAdd":                   lambda s, x: s.values.add(x) if isinstance(s, SetInstance) else s.add(x),
    "setRemove":                lambda s, x: s.values.remove(x) if isinstance(s, SetInstance) else s.remove(x),
    "setDiscard":               lambda s, x: s.values.discard(x) if isinstance(s, SetInstance) else s.discard(x),
    "setPop":                   lambda s: s.values.pop() if isinstance(s, SetInstance) else s.pop(),
    "setClear":                 lambda s: s.values.clear() if isinstance(s, SetInstance) else s.clear(),
    "setCopy":                  lambda s: SetInstance(set(s.values)) if isinstance(s, SetInstance) else s.copy(),
    "setUnion":                 lambda s, other: SetInstance(s.values.union(other.values if isinstance(other, SetInstance) else other)),
    "setIntersection":           lambda s, other: SetInstance(s.values.intersection(other.values if isinstance(other, SetInstance) else other)),
    "setDifference":             lambda s, other: SetInstance(s.values.difference(other.values if isinstance(other, SetInstance) else other)),
    "setSymmetricDifference":    lambda s, other: SetInstance(s.values.symmetric_difference(other.values if isinstance(other, SetInstance) else other)),
    "setUpdate":                 lambda s, other: s.values.update(other.values if isinstance(other, SetInstance) else other),
    "setIntersectionUpdate":     lambda s, other: s.values.intersection_update(other.values if isinstance(other, SetInstance) else other),
    "setDifferenceUpdate":       lambda s, other: s.values.difference_update(other.values if isinstance(other, SetInstance) else other),
    "setSymmetricDifferenceUpdate": lambda s, other: s.values.symmetric_difference_update(other.values if isinstance(other, SetInstance) else other),
    "setIsSubset":               lambda s, other: s.values.issubset(other.values if isinstance(other, SetInstance) else other),
    "setIsSuperset":             lambda s, other: s.values.issuperset(other.values if isinstance(other, SetInstance) else other),
    "setIsDisjoint":             lambda s, other: s.values.isdisjoint(other.values if isinstance(other, SetInstance) else other),
}

