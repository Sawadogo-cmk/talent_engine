# scoring.py
import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"


def charger_config():
    """Charge la configuration depuis config.json."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Chargé une fois au démarrage du module
CONFIG = charger_config()


def calculer_score_total(scores):
    """
    Calcule le score total pondéré à partir des scores par critère.
    Les poids sont lus dans config.json.
    """
    poids = CONFIG["poids"]
    total = sum(scores[k] * poids[k] for k in poids)
    return round(total, 2)


def determiner_priorite(score_total, score_tech):
    """
    Détermine la priorité d'examen d'un candidat selon les seuils de config.json.
    """
    seuils = CONFIG["seuils"]
    if score_total >= seuils["priorite_haute"] and score_tech >= seuils["tech_min_haute"]:
        return "Haute"
    elif score_total >= seuils["priorite_moyenne"]:
        return "Moyenne"
    return "Basse"