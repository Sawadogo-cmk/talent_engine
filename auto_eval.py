# auto_eval.py
from scoring import CONFIG


def evaluer_competences(competences_str):
    """
    Note les compétences sur 100 selon leur pertinence.
    + de compétences clés trouvées → score plus élevé.
    """
    if not competences_str:
        return 20

    comps = [c.strip().lower() for c in competences_str.split(",") if c.strip()]
    cles = [k.lower() for k in CONFIG["regles_auto"]["competences_cles"]]

    if not comps:
        return 20

    matches = sum(1 for c in comps if any(k in c for k in cles))
    ratio = matches / max(len(cles), 1)
    return min(100, int(30 + ratio * 70))


def evaluer_experience(annees):
    """
    Bonus progressif selon l'expérience, plafonné.
    """
    try:
        annees = int(annees)
    except (TypeError, ValueError):
        annees = 0

    bonus = min(
        annees * CONFIG["regles_auto"]["experience_bonus_par_an"],
        CONFIG["regles_auto"]["experience_max_bonus"]
    )
    return min(100, 40 + bonus)


def evaluer_disponibilite(dispo):
    """Convertit la disponibilité en score sur 100."""
    mapping = CONFIG["disponibilite_scores"]
    return mapping.get(dispo, 50)


def proposer_scores(candidat):
    """
    Renvoie un dict de scores suggérés à partir du profil d'un candidat.
    L'évaluateur peut ensuite ajuster manuellement.
    """
    return {
        "score_tech": evaluer_competences(candidat.get("competences", "")),
        "score_projet": evaluer_experience(candidat.get("experience", 0)),
        "score_motivation": 60,          # neutre, à ajuster manuellement
        "score_communication": 60,       # neutre, à ajuster manuellement
        "score_disponibilite": evaluer_disponibilite(candidat.get("disponibilite", ""))
    }