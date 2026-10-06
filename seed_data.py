# seed_data.py
import sqlite3
from datetime import datetime

DB_NAME = "talent_engine.db"

CANDIDATS = [
    {
        "nom": "Alice Dupont",
        "email": "alice.dupont@example.com",
        "telephone": "+229 97 12 34 56",
        "pays": "Bénin",
        "github": "https://github.com/alice-dev",
        "portfolio": "https://alice-dev.netlify.app",
        "motivation": "Passionnée par le développement backend et les API REST.",
        "competences": "Python, FastAPI, SQL, Docker, Git",
        "experience": 3,
        "disponibilite": "Immédiate"
    },
    {
        "nom": "Bob Traoré",
        "email": "bob.traore@example.com",
        "telephone": "+226 70 88 99 00",
        "pays": "Burkina Faso",
        "github": "https://github.com/bobtraore",
        "portfolio": "",
        "motivation": "Étudiant en L3 informatique, motivé pour apprendre.",
        "competences": "HTML, CSS, JavaScript",
        "experience": 0,
        "disponibilite": "3 mois"
    },
    {
        "nom": "Clarisse Mensah",
        "email": "clarisse.mensah@example.com",
        "telephone": "+228 90 45 67 89",
        "pays": "Togo",
        "github": "https://github.com/clarisse-m",
        "portfolio": "https://clarisse.dev",
        "motivation": "5 ans d'expérience en fullstack, je veux contribuer à des projets à impact.",
        "competences": "JavaScript, React, Node.js, TypeScript, GraphQL, Git, API",
        "experience": 5,
        "disponibilite": "1 mois"
    },
    {
        "nom": "David Kouassi",
        "email": "david.kouassi@example.com",
        "telephone": "+225 07 12 34 56",
        "pays": "Côte d'Ivoire",
        "github": "",
        "portfolio": "",
        "motivation": "Débutant autodidacte, très motivé.",
        "competences": "Python",
        "experience": 0,
        "disponibilite": "6 mois"
    },
    {
        "nom": "Eva Ndiaye",
        "email": "eva.ndiaye@example.com",
        "telephone": "+221 77 123 45 67",
        "pays": "Sénégal",
        "github": "https://github.com/eva-ndiaye",
        "portfolio": "https://eva-ml.io",
        "motivation": "Spécialiste ML, 4 ans d'expérience en production.",
        "competences": "Python, Machine Learning, TensorFlow, SQL, Docker, API, Git",
        "experience": 4,
        "disponibilite": "Immédiate"
    },
]


def seed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    ajoutes = 0
    for cand in CANDIDATS:
        try:
            c.execute('''
                INSERT INTO candidats
                (nom, email, telephone, pays, github, portfolio, motivation,
                 competences, experience, disponibilite, date_ajout)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cand["nom"], cand["email"], cand["telephone"], cand["pays"],
                cand["github"], cand["portfolio"], cand["motivation"],
                cand["competences"], cand["experience"], cand["disponibilite"],
                datetime.now().isoformat()
            ))
            ajoutes += 1
        except sqlite3.IntegrityError:
            print(f"⏭️  Déjà présent : {cand['email']}")

    conn.commit()
    conn.close()
    print(f"✅ {ajoutes} candidat(s) ajouté(s) sur {len(CANDIDATS)}.")


if __name__ == "__main__":
    seed()