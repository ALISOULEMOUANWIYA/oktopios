"""
parse_error.py — Erreurs de syntaxe Oktopios avec position précise.
"""


class OktopiosError(Exception):
    """Erreur de base du langage Oktopios."""

    def __init__(self, message, line=None, column=None, source=None):
        self.line = line
        self.column = column
        self.source = source
        super().__init__(self._format(message))

    def _format(self, message):
        parts = []
        if self.source:
            parts.append(self.source)
        if self.line is not None:
            loc = f"ligne {self.line}"
            if self.column is not None:
                loc += f", colonne {self.column}"
            parts.append(loc)
        prefix = " → ".join(parts)
        return f"[{prefix}] {message}" if prefix else message


class ParseError(OktopiosError):
    """Erreur levée pendant l'analyse syntaxique (parseur)."""
    pass


class LexError(OktopiosError):
    """Erreur levée pendant la tokenisation (lexeur)."""
    pass


class RuntimeError_(OktopiosError):
    """Erreur levée pendant l'exécution (interpréteur)."""
    pass

