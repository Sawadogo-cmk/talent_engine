# cv_parser.py
import re
import pdfplumber


# ============================================================
# EXTRACTION DU TEXTE BRUT
# ============================================================
def extraire_texte_pdf(fichier_pdf):
    """Extrait le texte brut d'un PDF page par page."""
    texte = ""
    try:
        with pdfplumber.open(fichier_pdf) as pdf:
            for page in pdf.pages:
                texte += (page.extract_text() or "") + "\n"
    except Exception as e:
        raise RuntimeError(f"Lecture PDF impossible : {e}")
    return texte.strip()


# ============================================================
# EXTRACTEURS PAR REGEX
# ============================================================
def extraire_email(texte):
    """Détecte la première adresse email du CV."""
    match = re.search(r"[\w\.\-\+]+@[\w\.\-]+\.\w+", texte)
    return match.group(0) if match else ""


def extraire_telephone(texte):
    """
    Détecte un numéro de téléphone international ou local.
    Ex : +226 46 29 48 37, +227 87284619, 06 12 34 56 78
    """
    match = re.search(r"(\+?\d[\d\s\-\.\(\)]{6,}\d)", texte)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(0)).strip()


def extraire_github(texte):
    """Détecte un lien GitHub."""
    match = re.search(
        r"https?://(?:www\.)?github\.com/[\w\-\.]+",
        texte, re.IGNORECASE
    )
    return match.group(0) if match else ""


def extraire_linkedin(texte):
    """Détecte un lien LinkedIn."""
    match = re.search(
        r"https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+",
        texte, re.IGNORECASE
    )
    return match.group(0) if match else ""


def extraire_portfolio(texte):
    """
    Détecte un site personnel (portfolio).
    Couvre : netlify.app, vercel.app, github.io, .dev, .me, .tech, .io
    """
    patterns = [
        r"https?://[\w\-]+\.netlify\.app",
        r"https?://[\w\-]+\.vercel\.app",
        r"https?://[\w\-]+\.github\.io",
        r"https?://[\w\-]+\.dev",
        r"https?://[\w\-]+\.me",
        r"https?://[\w\-]+\.tech",
        r"https?://[\w\-]+\.io",
    ]
    for p in patterns:
        match = re.search(p, texte, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""


def extraire_nom(texte):
    """
    Heuristique : prend la première ligne non vide qui ressemble à un nom.
    Critères : 2 à 4 mots, pas d'email, pas de chiffres, majuscules en début.
    """
    for ligne in texte.split("\n"):
        ligne = ligne.strip()
        if not ligne:
            continue
        if "@" in ligne or any(c.isdigit() for c in ligne):
            continue
        mots = ligne.split()
        if 2 <= len(mots) <= 4 and all(m[0].isupper() for m in mots if m):
            return " ".join(mots)
    return ""


def extraire_experience(texte):
    """
    Estime les années d'expérience professionnelle.

    Stratégie en deux temps :
    1. Cherche une mention explicite : 'X ans d'expérience', 'X years experience'
       → priorité maximale, on prend ce chiffre.
    2. Sinon, déduit à partir des années de projets mentionnées dans le CV
       (ex : projets en 2024, 2025, 2026 → 2 ans couverts).
    3. Sinon, retourne 0.
    """
    # 1. Recherche explicite
    match = re.search(
        r"(\d{1,2})\s*(?:\+)?\s*(?:ans?|years?)\s*(?:d['e]?\s*)?(?:exp|experience)",
        texte, re.IGNORECASE
    )
    if match:
        return int(match.group(1))

    # 2. Détection par années (2020 à 2039 pour couvrir large)
    annees = [int(a) for a in re.findall(r"\b(20[2-3]\d)\b", texte)]
    if annees:
        annee_min = min(annees)
        annee_max = max(annees)
        # Nombre d'années couvertes : 2024→2026 = 2 ans
        return max(0, annee_max - annee_min)

    # 3. Aucune information
    return 0


def extraire_competences(texte, mots_cles):
    """
    Détecte les compétences connues dans le texte (insensible à la casse).
    Retourne une liste triée selon l'ordre des mots-clés fournis.
    """
    texte_lower = texte.lower()
    trouvees = [m for m in mots_cles if m.lower() in texte_lower]
    return trouvees


# ============================================================
# ORCHESTRATEUR
# ============================================================
def parser_cv(fichier_pdf, mots_cles_competences):
    """
    Analyse un CV PDF et retourne un dict avec les champs extraits.
    Toutes les valeurs peuvent être vides ou approximatives —
    l'utilisateur ajustera manuellement avant l'enregistrement.
    """
    texte = extraire_texte_pdf(fichier_pdf)

    competences_liste = extraire_competences(texte, mots_cles_competences)
    competences_str = ", ".join(competences_liste)

    return {
        "texte_brut": texte,
        "nom": extraire_nom(texte),
        "email": extraire_email(texte),
        "telephone": extraire_telephone(texte),
        "github": extraire_github(texte),
        "linkedin": extraire_linkedin(texte),
        "portfolio": extraire_portfolio(texte),
        "experience": extraire_experience(texte),
        "competences": competences_str,
    }