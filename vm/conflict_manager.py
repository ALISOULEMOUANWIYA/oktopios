# =====================================================
# conflict_manager.py
# =====================================================

class ConflictManager:
    def __init__(self):
        # Dictionnaire : nom → provenance
        self.symbol_sources = {}

    def register_symbol(self, name: str, source: str):
        """Ajoute un symbole et vérifie les doublons."""
        if name in self.symbol_sources:
            existing_source = self.symbol_sources[name]
            raise Exception(
                f"[Conflit] Le symbole '{name}' est déjà défini ({existing_source}) "
                f"et entre en conflit avec la nouvelle définition ({source})."
            )
        self.symbol_sources[name] = source

    def remove_symbol(self, name: str):
        """Supprime un symbole (si un module est déchargé)."""
        if name in self.symbol_sources:
            del self.symbol_sources[name]
