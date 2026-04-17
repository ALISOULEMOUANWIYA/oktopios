# native_advanced_collections.py
from bisect import bisect_left, bisect_right, insort

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
