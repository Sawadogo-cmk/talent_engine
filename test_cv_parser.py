# test_cv_parser.py
from cv_parser import (
    extraire_email,
    extraire_telephone,
    extraire_github,
    extraire_linkedin,
    extraire_portfolio,
    extraire_nom,
    extraire_experience,
    extraire_competences,
)


# ============================================================
# TEXTE DE TEST GLOBAL
# ============================================================
TEXTE_TEST = """
Sawadogo Noe
Développeur Fullstack
Email : noesawadogo46@gmail.com
Téléphone : +227 87 28 46 19
GitHub : https://github.com/Sawadogo-cmk
LinkedIn : https://linkedin.com/in/sawadogo-noe
Portfolio : https://portfolio-sawadogo-noe.netlify.app/

3 ans d'expérience en développement web.
Compétences : Python, JavaScript, React, Git, SQL, Node.js
"""


# ============================================================
# TESTS D'EXTRACTION — CAS GÉNÉRAUX
# ============================================================
def test_email():
    assert extraire_email(TEXTE_TEST) == "noesawadogo46@gmail.com"


def test_telephone():
    tel = extraire_telephone(TEXTE_TEST)
    assert "+227" in tel and "87" in tel


def test_github():
    assert extraire_github(TEXTE_TEST) == "https://github.com/Sawadogo-cmk"


def test_linkedin():
    assert "linkedin.com/in/sawadogo-noe" in extraire_linkedin(TEXTE_TEST)


def test_portfolio():
    assert "netlify.app" in extraire_portfolio(TEXTE_TEST)


def test_nom():
    assert extraire_nom(TEXTE_TEST) == "Sawadogo Noe"


def test_competences():
    mots_cles = ["python", "javascript", "react", "sql", "git", "node"]
    comps = extraire_competences(TEXTE_TEST, mots_cles)
    assert "python" in comps
    assert "react" in comps
    assert "git" in comps


# ============================================================
# TESTS D'EXPÉRIENCE
# ============================================================
def test_experience_explicite():
    """Cas simple : '5 ans d'expérience'."""
    texte = "5 ans d'expérience en développement"
    assert extraire_experience(texte) == 5


def test_experience_par_annees_projets():
    """Pas de mention explicite → on déduit des années de projets."""
    texte = """
    Projet A - 2024
    Projet B - 2025
    Projet C - 2026
    """
    assert extraire_experience(texte) == 2


def test_experience_aucune_info():
    """Aucune info → 0."""
    texte = "Développeur passionné, aucune date."
    assert extraire_experience(texte) == 0


def test_experience_mention_prioritaire():
    """
    Si '3 ans d'expérience' ET des années projets sont présents,
    la mention explicite gagne.
    """
    texte = "3 ans d'expérience. Projets en 2020, 2024, 2026."
    assert extraire_experience(texte) == 3


def test_experience_une_seule_annee():
    """Une seule année citée → 0 an couvert."""
    texte = "Projet réalisé en 2025."
    assert extraire_experience(texte) == 0


def test_experience_anglais():
    """Détection de la version anglaise."""
    texte = "5 years experience in backend development"
    assert extraire_experience(texte) == 5


# ============================================================
# TESTS DE CAS LIMITES (entrées vides ou invalides)
# ============================================================
def test_texte_vide():
    assert extraire_email("") == ""
    assert extraire_nom("") == ""
    assert extraire_experience("") == 0
    assert extraire_github("") == ""
    assert extraire_linkedin("") == ""
    assert extraire_portfolio("") == ""


def test_competences_liste_vide():
    assert extraire_competences("", ["python", "react"]) == []


def test_competences_aucune_correspondance():
    texte = "Je suis éleveur de poulets."
    assert extraire_competences(texte, ["python", "react"]) == []


def test_nom_ignore_lignes_avec_chiffres():
    """La première ligne contient un numéro → on passe à la suivante."""
    texte = """
    12345
    Sawadogo Noe
    """
    assert extraire_nom(texte) == "Sawadogo Noe"


def test_nom_ignore_lignes_avec_email():
    """La première ligne contient un email → on passe à la suivante."""
    texte = """
    contact@example.com
    Alice Dupont
    """
    assert extraire_nom(texte) == "Alice Dupont"