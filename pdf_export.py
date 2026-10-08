# pdf_export.py
from fpdf import FPDF
from datetime import datetime


class RapportClassement(FPDF):
    """Génère un PDF de classement des candidats."""

    def header(self):
        # Bandeau en haut
        self.set_fill_color(30, 60, 120)  # bleu foncé
        self.rect(0, 0, 210, 20, "F")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.set_y(6)
        self.cell(0, 8, "Talent Engine - SKULLVI", ln=True, align="C")

        # Sous-titre
        self.set_y(22)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(
            0, 5,
            f"Rapport de classement - généré le {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
            ln=True, align="C"
        )
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _priorite_couleur(priorite):
    """Retourne (fond, texte) selon la priorité."""
    if priorite == "Haute":
        return (220, 245, 220), (30, 120, 30)      # vert clair / vert foncé
    elif priorite == "Moyenne":
        return (255, 245, 220), (180, 120, 0)       # orange clair / orange
    else:
        return (245, 220, 220), (160, 30, 30)       # rouge clair / rouge


def generer_pdf_classement(df_evalues, chemin="classement_skullvi.pdf"):
    """
    Génère un PDF de classement à partir d'un DataFrame évalué.
    df_evalues : DataFrame trié par score_total décroissant
    chemin : chemin du fichier PDF à générer
    """
    pdf = RapportClassement()
    pdf.add_page()

    # ---- En-tête du tableau ----
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(30, 60, 120)
    pdf.set_text_color(255, 255, 255)

    largeurs = [10, 45, 60, 35, 25]  # Rang, Nom, Email, Pays, Score
    entetes = ["#", "Nom", "Email", "Pays", "Score"]

    for largeur, entete in zip(largeurs, entetes):
        pdf.cell(largeur, 8, entete, border=0, fill=True, align="C")
    pdf.ln()

    # ---- Lignes ----
    pdf.set_font("Helvetica", "", 9)
    rang = 1

    for _, row in df_evalues.iterrows():
        fond, texte = _priorite_couleur(str(row.get("priorite", "")))

        pdf.set_fill_color(*fond)
        pdf.set_text_color(*texte)

        # Rang
        pdf.cell(largeurs[0], 7, str(rang), border="B", fill=True, align="C")

        # Nom
        pdf.set_text_color(0, 0, 0)
        nom = str(row.get("nom", ""))[:30]  # tronquer si trop long
        pdf.cell(largeurs[1], 7, nom, border="B", align="L")

        # Email
        email = str(row.get("email", ""))[:40]
        pdf.cell(largeurs[2], 7, email, border="B", align="L")

        # Pays
        pays = str(row.get("pays", ""))[:20]
        pdf.cell(largeurs[3], 7, pays, border="B", align="L")

        # Score
        pdf.set_text_color(*texte)
        score = f"{row.get('score_total', 0):.1f}"
        pdf.cell(largeurs[4], 7, score, border="B", fill=True, align="C")
        pdf.ln()

        rang += 1

    # ---- Synthèse ----
    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(30, 60, 120)
    pdf.cell(0, 8, "Synthese", ln=True)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    total = len(df_evalues)
    haute = len(df_evalues[df_evalues["priorite"] == "Haute"])
    moyenne = len(df_evalues[df_evalues["priorite"] == "Moyenne"])
    basse = len(df_evalues[df_evalues["priorite"] == "Basse"])
    score_moyen = df_evalues["score_total"].mean()

    pdf.cell(0, 6, f"Candidats evalues : {total}", ln=True)
    pdf.cell(0, 6, f"Score moyen : {score_moyen:.1f} / 100", ln=True)
    pdf.ln(2)

    pdf.set_text_color(30, 120, 30)
    pdf.cell(0, 6, f"- Priorite HAUTE   : {haute}", ln=True)
    pdf.set_text_color(180, 120, 0)
    pdf.cell(0, 6, f"- Priorite MOYENNE : {moyenne}", ln=True)
    pdf.set_text_color(160, 30, 30)
    pdf.cell(0, 6, f"- Priorite BASSE   : {basse}", ln=True)

    pdf.output(chemin)
    return chemin