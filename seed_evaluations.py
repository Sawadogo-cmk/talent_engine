# seed_evaluations.py
import sqlite3
from datetime import datetime

DB_NAME = "talent_engine.db"

EVALUATIONS = [
    # email, tech, projet, motivation, communication, disponibilite, commentaire
    ("alice.dupont@example.com",     85, 75, 70, 65, 100, "Très bon profil backend"),
    ("bob.traore@example.com",       45, 30, 70, 55,  65, "Junior motivé, à former"),
    ("clarisse.mensah@example.com",  90, 95, 80, 85,  85, "Senior confirmée, top profil"),
    ("david.kouassi@example.com",    30, 20, 60, 40,  45, "Trop junior pour le programme"),
    ("eva.ndiaye@example.com",       95, 90, 85, 80, 100, "Excellente, expertise ML rare"),
]


def calculer_score(tech, projet, motivation, communication, dispo):
    return round(
        tech * 0.30 + projet * 0.25 + motivation * 0.20 +
        communication * 0.15 + dispo * 0.10, 2
    )


def determiner_priorite(total, tech):
    if total >= 80 and tech >= 70:
        return "Haute"
    elif total >= 60:
        return "Moyenne"
    return "Basse"


def seed():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    for email, tech, projet, moti, comm, dispo, commentaire in EVALUATIONS:
        # Récupérer l'id
        c.execute("SELECT id FROM candidats WHERE email = ?", (email,))
        row = c.fetchone()
        if not row:
            print(f"⏭️  Candidat introuvable : {email}")
            continue

        cid = row[0]
        total = calculer_score(tech, projet, moti, comm, dispo)
        priorite = determiner_priorite(total, tech)

        c.execute('''
            INSERT OR REPLACE INTO evaluations
            (candidat_id, score_tech, score_projet, score_motivation,
             score_communication, score_disponibilite, score_total,
             priorite, commentaire, date_eval)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cid, tech, projet, moti, comm, dispo,
            total, priorite, commentaire, datetime.now().isoformat()
        ))
        print(f"✅ {email} → {total}/100 ({priorite})")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed()