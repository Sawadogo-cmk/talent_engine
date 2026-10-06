# test_scoring.py
from scoring import calculer_score_total, determiner_priorite

def test_calculer_score_total():
    scores = {
        'score_tech': 90,
        'score_projet': 80,
        'score_motivation': 70,
        'score_communication': 60,
        'score_disponibilite': 50
    }
    # 90*0.3 + 80*0.25 + 70*0.2 + 60*0.15 + 50*0.1 = 27 + 20 + 14 + 9 + 5 = 75
    assert calculer_score_total(scores) == 75.0

def test_determiner_priorite_haute():
    assert determiner_priorite(85, 75) == "Haute"

def test_determiner_priorite_moyenne_tech_faible():
    assert determiner_priorite(85, 65) == "Moyenne"  # tech < 70

def test_determiner_priorite_moyenne_score_moyen():
    assert determiner_priorite(70, 80) == "Moyenne"

def test_determiner_priorite_basse():
    assert determiner_priorite(50, 50) == "Basse"