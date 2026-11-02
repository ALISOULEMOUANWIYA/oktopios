"""
suggestions.py — Suggestions « Vouliez-vous dire ? » pour les messages d'erreur.

Quand un nom est introuvable (variable, fonction, namespace natif ou fonction
d'un namespace), l'interpréteur appelle `did_you_mean()` pour proposer le
candidat le plus proche (distance de Levenshtein, insensible à la casse).

Aucune dépendance externe.
"""


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def closest_name(name, candidates, max_distance=None):
    """Retourne le candidat le plus proche de `name`, ou None si aucun n'est assez proche.

    Seuil par défaut : 1 pour les noms de ≤ 3 caractères, 2 jusqu'à 6, puis 3.
    Les clés internes de la forme `nom/arité` sont normalisées en `nom`.
    """
    name = str(name)
    if max_distance is None:
        n = len(name)
        max_distance = 1 if n <= 3 else 2 if n <= 6 else 3

    best, best_d = None, None
    seen = set()
    low = name.lower()
    for cand in candidates:
        if not isinstance(cand, str):
            continue
        cand = cand.split("/", 1)[0]
        if not cand or cand == name or cand in seen or cand.startswith("__"):
            continue
        seen.add(cand)
        d = _levenshtein(low, cand.lower())
        # Une simple différence de casse compte comme la meilleure suggestion possible
        if d == 0:
            d = 0.5
        if d <= max_distance and (best_d is None or d < best_d or (d == best_d and cand < best)):
            best, best_d = cand, d
    return best


def did_you_mean(name, candidates, max_distance=None) -> str:
    """Retourne un suffixe de message « Vouliez-vous dire 'x' ? » (ou chaîne vide)."""
    match = closest_name(name, candidates, max_distance)
    return f" — Vouliez-vous dire '{match}' ?" if match else ""


def env_names(env):
    """Collecte tous les noms visibles depuis un Environment (chaîne enclosing comprise)."""
    names = []
    seen_envs = set()
    while env is not None and id(env) not in seen_envs:
        seen_envs.add(id(env))
        names.extend(getattr(env, "values", {}).keys())
        env = getattr(env, "enclosing", None)
    return names
