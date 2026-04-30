from itertools import product


# =====================================================
# Cellule atomique
# =====================================================

class MatrixCell:
    def __init__(self, coord, value=0):
        self.coord = tuple(coord)
        self.value = value
        self.dimension_links = {}     # {dim: MatrixCell}
        self.external_links = set()   # connexions libres vers autres cellules

    def link_external(self, other):
        if not isinstance(other, MatrixCell):
            raise TypeError("External link must target a MatrixCell")
        self.external_links.add(other)


# =====================================================
# Matrice N-dimensionnelle chainée
# =====================================================

class Matrix:

    # -------------------------------------------------
    # Constructeur
    # -------------------------------------------------

    def __init__(self, shape, dense=True):
        if not shape:
            raise ValueError("Shape cannot be empty")

        self.shape = tuple(shape)
        self.dim = len(shape)
        self.cells = {}

        if dense:
            self._build_dense()


    # -------------------------------------------------
    # Construction dense
    # -------------------------------------------------

    def _build_dense(self):
        for coord in product(*[range(s) for s in self.shape]):
            self.cells[coord] = MatrixCell(coord)

        self._link_dimensions()


    # -------------------------------------------------
    # Liaison interne dimensionnelle
    # -------------------------------------------------

    def _link_dimensions(self):
        for coord, cell in self.cells.items():
            for d in range(self.dim):
                neighbor = list(coord)

                if neighbor[d] + 1 < self.shape[d]:
                    neighbor[d] += 1
                    cell.dimension_links[d] = self.cells[tuple(neighbor)]


    # -------------------------------------------------
    # Accès sécurisé
    # -------------------------------------------------

    def _validate_coord(self, coord):
        if len(coord) != self.dim:
            raise ValueError("Invalid coordinate dimension")

        for i, val in enumerate(coord):
            if val < 0 or val >= self.shape[i]:
                raise IndexError("Coordinate out of bounds")


    def get(self, coord):
        coord = tuple(coord)
        self._validate_coord(coord)
        return self.cells[coord].value


    def set(self, coord, value):
        coord = tuple(coord)
        self._validate_coord(coord)
        self.cells[coord].value = value


    # -------------------------------------------------
    # Parcours sécurisé (anti-boucle)
    # -------------------------------------------------

    def safe_iter(self):
        visited = set()
        stack = list(self.cells.values())

        while stack:
            cell = stack.pop()
            if id(cell) in visited:
                continue

            visited.add(id(cell))
            yield cell

            for nxt in cell.dimension_links.values():
                stack.append(nxt)

            for ext in cell.external_links:
                stack.append(ext)


    # =================================================
    # OPERATIONS MATHEMATIQUES
    # =================================================

    # -------------------------------------------------
    # Addition
    # -------------------------------------------------

    @staticmethod
    def add(A, B, preserve_links=True):

        if A.shape != B.shape:
            raise ValueError("Shape mismatch for addition")

        C = Matrix(A.shape)

        for coord in A.cells:
            C.cells[coord].value = (
                A.cells[coord].value +
                B.cells[coord].value
            )

        if preserve_links:
            for coord in A.cells:
                C.cells[coord].external_links = \
                    A.cells[coord].external_links.copy()

        return C


    # -------------------------------------------------
    # Produit tensoriel
    # -------------------------------------------------

    @staticmethod
    def tensor(A, B):

        new_shape = A.shape + B.shape
        C = Matrix(new_shape)

        for coordA, cellA in A.cells.items():
            for coordB, cellB in B.cells.items():
                coordC = coordA + coordB
                C.cells[coordC].value = cellA.value * cellB.value

        return C


    # -------------------------------------------------
    # Contraction N-dimensionnelle
    # -------------------------------------------------

    def __repr__(self):
        lines = []
        for coord in sorted(self.cells.keys()):
            v = self.cells[coord].value
            if v != 0:
                lines.append(f"  {coord} -> {v}")
        body = "\n".join(lines) if lines else "  (vide)"
        return f"Matrix{list(self.shape)}:\n{body}"

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def contract(A, B, dimA, dimB):

        if dimA >= A.dim or dimB >= B.dim:
            raise ValueError("Invalid contraction dimension")

        if A.shape[dimA] != B.shape[dimB]:
            raise ValueError("Dimension mismatch for contraction")

        new_shape = (
            A.shape[:dimA] +
            A.shape[dimA + 1:] +
            B.shape[:dimB] +
            B.shape[dimB + 1:]
        )

        C = Matrix(new_shape)

        for coordC in C.cells:

            total = 0

            for k in range(A.shape[dimA]):

                coordA = (
                    coordC[:dimA] +
                    (k,) +
                    coordC[dimA:dimA + A.dim - dimA - 1]
                )

                offset = A.dim - 1
                coordB = (
                    coordC[offset:offset + dimB] +
                    (k,) +
                    coordC[offset + dimB:]
                )

                total += (
                    A.cells[coordA].value *
                    B.cells[coordB].value
                )

            C.cells[coordC].value = total

        return C

