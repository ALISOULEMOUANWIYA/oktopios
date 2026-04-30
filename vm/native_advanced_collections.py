# native_advanced_collections.py
from bisect import bisect_left, bisect_right, insort
import uuid
from collections import deque
# -----------------------------
# LinkedList (doublement chaînée)
# -----------------------------
class LinkedListNode:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

class LinkedListInstance:
    def __init__(self, iterable=None):
        self.head = None
        self.tail = None
        self.size = 0
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, value):
        if type(value) == list:
            for item in value:
                self.addItem(item)
        else:
            self.addItem(value)

    def addItem(self, value):
        node = LinkedListNode(value)
        if not self.head:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove(self, value):
        current = self.head
        while current:
            if current.value == value:
                if current.prev:
                    current.prev.next = current.next
                else:
                    self.head = current.next
                if current.next:
                    current.next.prev = current.prev
                else:
                    self.tail = current.prev
                self.size -= 1
                return True
            current = current.next
        return False

    def to_list(self):
        res = []
        current = self.head
        while current:
            res.append(current.value)
            current = current.next
        return res

# -----------------------------
# TreeSet (tri automatique)
# -----------------------------
class TreeSetInstance:
    def __init__(self, iterable=None):
        self.values = []
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, value):
        if value not in self.values:
            insort(self.values, value)

    def remove(self, value):
        if value in self.values:
            self.values.remove(value)

    def contains(self, value):
        return value in self.values

    def to_list(self):
        return list(self.values)

# -----------------------------
# LinkedHashSet (ordre d'insertion)
# -----------------------------
class LinkedHashSetInstance:
    def __init__(self, iterable=None):
        self.values = dict()
        if iterable:
            for item in iterable:
                self.add(item)

    def add(self, value):
        self.values[value] = None

    def remove(self, value):
        if value in self.values:
            del self.values[value]

    def contains(self, value):
        return value in self.values

    def to_list(self):
        return list(self.values.keys())

# -----------------------------
# TreeMap (dictionnaire trié par clé)
# -----------------------------
class TreeMapInstance:
    def __init__(self, init=None):
        self.values = dict()
        self.keys_sorted = []
        if init is not None:
            for k, v in dict(init).items():
                self.put(k, v)


    def put(self, key, value):
        if key not in self.values:
            insort(self.keys_sorted, key)
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def remove(self, key):
        if key in self.values:
            self.keys_sorted.remove(key)
            del self.values[key]

    def keys(self):
        return list(self.keys_sorted)

    def values_list(self):
        return [self.values[k] for k in self.keys_sorted]

# -----------------------------
# Fonctions utilitaires
# -----------------------------
def swap(lst, i, j):
    lst[i], lst[j] = lst[j], lst[i]

def reverseOrder(lst):
    return sorted(lst, reverse=True)

def binarySearch(lst, value):
    idx = bisect_left(lst, value)
    if idx != len(lst) and lst[idx] == value:
        return idx
    return -1

# -----------------------------
# Iterator pour Oktopios
# -----------------------------
class IteratorInstance:
    def __init__(self, iterable):
        self.iterable = iterable
        self.index = 0

    def hasNext(self):
        return self.index < len(self.iterable)

    def next(self):
        if not self.hasNext():
            raise StopIteration("Iterator has no more elements")
        value = self.iterable[self.index]
        self.index += 1
        return value


# ==============================
# MATRIX N-D CHAINED STRUCTURE
# ==============================

class LinkObject:
    def __init__(self, source, target, metadata=None, directed=False):
        self.id = uuid.uuid4()
        self.source = source
        self.target = target
        self.metadata = metadata or {}
        self.directed = directed

class CellObject:
    def __init__(self, coords, parent):
        self.coords = tuple(coords)
        self.value = None
        self.parent = parent
        self.links = []

    def __repr__(self):
        return f"Cell({list(self.coords)}, val={self.value})"

    def __str__(self):
        return self.__repr__()

class MatrixObject:
    def __init__(self, shape, dense=False):
        self.id = uuid.uuid4()
        self.shape = tuple(shape)
        self.ndim = len(shape)
        self.is_dense = dense
        self.cells = {}

    def _check(self, coords):
        if len(coords) != self.ndim:
            raise Exception("Matrix dimension mismatch")
        for i, c in enumerate(coords):
            if c < 0 or c >= self.shape[i]:
                raise Exception("Matrix index out of bounds")

    def __repr__(self):
        cells = {str(list(k)): v.value for k, v in self.cells.items() if v.value is not None}
        return f"MatrixObject{list(self.shape)}: {cells}"

    def __str__(self):
        return self.__repr__()

    def _get_cell(self, coords, create=False):
        coords = tuple(coords)
        if coords in self.cells:
            return self.cells[coords]
        if not create:
            return None
        cell = CellObject(coords, self)
        self.cells[coords] = cell
        return cell

    def set(self, coords, value):
        self._check(coords)
        cell = self._get_cell(coords, True)
        cell.value = value
        return value

    def get(self, coords):
        self._check(coords)
        cell = self._get_cell(coords)
        return None if cell is None else cell.value

    def link(self, coordsA, other, coordsB, metadata=None, directed=False):
        cA = self._get_cell(coordsA, True)
        cB = other._get_cell(coordsB, True)

        link = LinkObject(cA, cB, metadata, directed)
        cA.links.append(link)

        if not directed:
            reverse = LinkObject(cB, cA, metadata, directed)
            cB.links.append(reverse)

        return link

    def traverse(self, start_coords, strategy="dfs"):
        start = self._get_cell(start_coords)
        if not start:
            return []

        visited = set()
        result = []

        if strategy == "bfs":
            queue = deque([start])
            while queue:
                node = queue.popleft()
                key = (node.parent.id, node.coords)
                if key in visited:
                    continue
                visited.add(key)
                result.append(node)

                for link in node.links:
                    queue.append(link.target)
        else:
            stack = [start]
            while stack:
                node = stack.pop()
                key = (node.parent.id, node.coords)
                if key in visited:
                    continue
                visited.add(key)
                result.append(node)

                for link in node.links:
                    stack.append(link.target)

        return result

    def detect_cycle(self, start_coords):
        start = self._get_cell(start_coords)
        if not start:
            return False

        visited = set()
        stack = set()

        def dfs(node):
            key = (node.parent.id, node.coords)
            if key in stack:
                return True
            if key in visited:
                return False

            visited.add(key)
            stack.add(key)

            for link in node.links:
                if dfs(link.target):
                    return True

            stack.remove(key)
            return False

        return dfs(start)



