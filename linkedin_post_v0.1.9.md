# LinkedIn Post — Oktopios v0.1.9 🐙

> **Image à joindre :** `oktopios_v0.1.9_linkedin.png`

---

## 🇫🇷 Version française

🐙 **Oktopios v0.1.9 est disponible !**

Deux nouvelles structures de données **natives** viennent d'être ajoutées au langage :

📬 **Queue** — file d'attente FIFO
🗂️ **Stack** — pile LIFO

```okp
var q = Queue.create()
Queue.enqueue(q, "Alice")
Queue.enqueue(q, "Bob")
print(Queue.dequeue(q))   // Alice  ← premier arrivé, premier servi

var s = Stack.create([1, 2, 3])
Stack.push(s, 99)
print(Stack.pop(s))       // 99  ← dernier entré, premier sorti
print(Stack.toList(s))    // [3, 2, 1]  — sommet en premier
```

Chaque namespace offre **10 fonctions** : `create`, `fromList`, `peek`, `size`, `isEmpty`, `contains`, `toList`, `clear` + les opérations caractéristiques (`enqueue`/`dequeue` ou `push`/`pop`).

Queue et Stack complètent la bibliothèque de collections Oktopios aux côtés de `List`, `Map`, `Set` — tout ce qu'il faut pour des algorithmes classiques (BFS, DFS, undo-redo, traitement en file…) sans dépendances externes.

🔗 GitHub : https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI : `pip install --upgrade oktopios`

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #DataStructures #Queue #Stack

---

## 🇬🇧 English version

🐙 **Oktopios v0.1.9 is out!**

Two new **native** data structure namespaces have landed in the language:

📬 **Queue** — FIFO data structure
🗂️ **Stack** — LIFO data structure

```okp
var q = Queue.create()
Queue.enqueue(q, "Alice")
Queue.enqueue(q, "Bob")
print(Queue.dequeue(q))   // Alice  ← first in, first out

var s = Stack.create([1, 2, 3])
Stack.push(s, 99)
print(Stack.pop(s))       // 99  ← last in, first out
print(Stack.toList(s))    // [3, 2, 1]  — top first
```

Each namespace ships **10 functions**: `create`, `fromList`, `peek`, `size`, `isEmpty`, `contains`, `toList`, `clear` — plus the characteristic operations (`enqueue`/`dequeue` or `push`/`pop`).

Queue and Stack join `List`, `Map`, and `Set` to complete Oktopios's native collections suite — everything you need for classic algorithms (BFS, DFS, undo-redo, task queues…) with zero external dependencies.

🔗 GitHub: https://github.com/ALISOULEMOUANWIYA/oktopios
📦 PyPI: `pip install --upgrade oktopios`

#OpenSource #Oktopios #Python #ProgrammingLanguage #IA #DataStructures #Queue #Stack
