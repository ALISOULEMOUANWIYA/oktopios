from .native_collections import (
    ListInstance,
    TupleInstance,
    MapInstance,
    SetInstance
)
from .native_advanced_collections import (
    LinkedListInstance,
    TreeSetInstance,
    LinkedHashSetInstance,
    TreeMapInstance,
    MatrixObject
)
from .matrix import Matrix
# -------------------------------
# constructeur natives
# -------------------------------
NativeCollectionsConstruct = {
    # =====================================================
    # --- Constructeurs de collections natives tipique python---
    # =====================================================
    "Lists": lambda init=None: ListInstance(list(init) if init is not None else []),
    "Tuples": lambda init=None: TupleInstance(tuple(init) if init is not None else ()),
    "Sets":   lambda init=None: SetInstance(set(init) if init is not None else set()),
    "Dists":  lambda init=None: MapInstance(dict(init) if init is not None else {}),

    # =====================================================
    # --- Constructeurs de collections natives tipique java---
    # =====================================================
    "LinkedList": lambda init=None: LinkedListInstance(list(init) if init is not None else []),
    "TreeSet": lambda init=None: TreeSetInstance(list(init) if init is not None else []),
    "LinkedHashSet": lambda init=None: LinkedHashSetInstance(list(init) if init is not None else []),
    "TreeMap": lambda init=None: TreeMapInstance(init),
    "Matrix": lambda shape, dense=False: Matrix(shape) if dense else MatrixObject(shape, False),

    # =====================================================
    # --- Constructeurs de collections natives tipique python---
    # =====================================================
    "input": lambda prompt=None: input(prompt or ""),
    "inputInt": lambda prompt=None: int(input(prompt or "")),
    "inputFloat": lambda prompt=None: float(input(prompt or "")),
}

