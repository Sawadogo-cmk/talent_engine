# app.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

from scoring import calculer_score_total, determiner_priorite
from auto_eval import proposer_scores
from cv_parser import parser_cv
from scoring import CONFIG

DB_NAME = "talent_engine.db"


# ============================================================
# BASE DE DONNÉES
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            email TEXT UNIQUE,
            telephone TEXT,
            pays TEXT,
            github TEXT,
            portfolio TEXT,
            motivation TEXT,
            competences TEXT,
            experience INTEGER,
            disponibilite TEXT,
            date_ajout TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            candidat_id INTEGER PRIMARY KEY,
            score_tech REAL,
            score_projet REAL,
            score_motivation REAL,
            score_communication REAL,
            score_disponibilite REAL,
            score_total REAL,
            priorite TEXT,
            commentaire TEXT,
            date_eval TEXT,
            FOREIGN KEY(candidat_id) REFERENCES candidats(id)
        )
    ''')
    conn.commit()
    conn.close()


def seed_si_vide():
    """
    Insère des données de démonstration si la base est vide.
    Utile notamment sur Streamlit Cloud, où la base est recréée
    à chaque redéploiement.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM candidats")
        count = c.fetchone()[0]
        conn.close()

        if count == 0:
            from seed_data import seed as seed_candidats
            from seed_evaluations import seed as seed_evals
            seed_candidats()
            seed_evals()
            print("✅ Données de démonstration insérées automatiquement.")
    except Exception as e:
        # On ne bloque pas l'app si le seed échoue
        print(f"⚠️ Seed automatique ignoré : {e}")


def ajouter_candidat(nom, email, telephone, pays, github, portfolio,
                     motivation, competences, experience, disponibilite):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO candidats
            (nom, email, telephone, pays, github, portfolio, motivation,
             competences, experience, disponibilite, date_ajout)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(nom), str(email), str(telephone), str(pays),
            str(github), str(portfolio), str(motivation),
            str(competences), int(experience), str(disponibilite),
            datetime.now().isoformat()
        ))
        conn.commit()
        return True, "Candidat ajouté avec succès."
    except sqlite3.IntegrityError:
        return False, "Cet email est déjà utilisé."
    finally:
        conn.close()


def get_candidats():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM candidats", conn)
    conn.close()
    return df


def get_evaluation(candidat_id):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        f"SELECT * FROM evaluations WHERE candidat_id = {int(candidat_id)}", conn
    )
    conn.close()
    return df


def enregistrer_evaluation(candidat_id, scores, commentaire):
    score_total = calculer_score_total(scores)
    priorite = determiner_priorite(score_total, scores['score_tech'])

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO evaluations
        (candidat_id, score_tech, score_projet, score_motivation,
         score_communication, score_disponibilite, score_total,
         priorite, commentaire, date_eval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        int(candidat_id),
        float(scores['score_tech']),
        float(scores['score_projet']),
        float(scores['score_motivation']),
        float(scores['score_communication']),
        float(scores['score_disponibilite']),
        float(score_total),
        str(priorite),
        str(commentaire) if commentaire else "",
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return score_total, priorite


def get_classement():
    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT c.id, c.nom, c.email, c.pays, c.competences, c.experience,
               e.score_tech, e.score_projet, e.score_motivation,
               e.score_communication, e.score_disponibilite,
               e.score_total, e.priorite, e.commentaire
        FROM candidats c
        LEFT JOIN evaluations e ON c.id = e.candidat_id
        ORDER BY e.score_total DESC NULLS LAST
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# ============================================================
# GESTION DES CANDIDATS
# ============================================================
def supprimer_candidat(candidat_id):
    """Supprime un candidat et son évaluation associée."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM evaluations WHERE candidat_id = ?", (int(candidat_id),))
    c.execute("DELETE FROM candidats WHERE id = ?", (int(candidat_id),))
    conn.commit()
    conn.close()


def reinitialiser_evaluations():
    """Efface toutes les évaluations mais garde les candidats."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM evaluations")
    conn.commit()
    conn.close()


def reinitialiser_tout():
    """Efface tous les candidats et toutes les évaluations."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM evaluations")
    c.execute("DELETE FROM candidats")
    conn.commit()
    conn.close()


# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(page_title="Talent Engine - SKULLVI", layout="wide")
st.title("Talent Engine - SKULLVI")

init_db()
seed_si_vide()

menu = [
    "Accueil",
    "Ajouter un candidat",
    "Évaluer un candidat",
    "Classement & Priorités",
    "Gérer les candidats",
]
choix = st.sidebar.selectbox("Menu", menu)


# ============================================================
# ACCUEIL
# ============================================================
if choix == "Accueil":
    st.markdown("""
    ## Bienvenue dans le Talent Engine

    Cette application permet de :
    - Recevoir les candidatures
    - Collecter les informations essentielles
    - Qualifier les profils
    - Attribuer un score
    - Classer les candidats
    - Identifier les profils à examiner en priorité

    👉 Utilisez le menu à gauche pour naviguer.
    """)


# ============================================================
# AJOUTER UN CANDIDAT (avec import CV PDF)
# ============================================================
elif choix == "Ajouter un candidat":
    st.header("Ajouter un candidat")

    # --- Import CV optionnel ---
    st.subheader("📄 Import automatique depuis un CV (optionnel)")
    st.caption(
        "Déposez un CV au format PDF : les champs seront pré-remplis "
        "automatiquement par extraction (regex). Vérifiez ensuite les valeurs."
    )

    cv_file = st.file_uploader("CV au format PDF", type=["pdf"], key="cv_uploader")

    if "cv_prefill" not in st.session_state:
        st.session_state.cv_prefill = {
            "nom": "", "email": "", "telephone": "",
            "github": "", "portfolio": "",
            "experience": 0, "competences": "",
            "texte_brut": ""
        }
        st.session_state.cv_parsed_name = None

    if cv_file is not None and st.session_state.get("cv_parsed_name") != cv_file.name:
        with st.spinner("Analyse du CV en cours..."):
            try:
                result = parser_cv(cv_file, CONFIG["regles_auto"]["competences_cles"])
                st.session_state.cv_prefill = result
                st.session_state.cv_parsed_name = cv_file.name
                st.success(
                    "✅ CV analysé. Vérifiez et corrigez les champs "
                    "ci-dessous avant d'enregistrer."
                )
                with st.expander("Voir le texte brut extrait du CV"):
                    st.text(result["texte_brut"][:3000] or "(aucun texte extrait)")
            except Exception as e:
                st.error(f"❌ Impossible d'analyser le CV : {e}")
                st.info("Vous pouvez remplir le formulaire manuellement ci-dessous.")

    if cv_file is None and st.session_state.cv_prefill.get("texte_brut"):
        st.session_state.cv_prefill = {
            "nom": "", "email": "", "telephone": "",
            "github": "", "portfolio": "",
            "experience": 0, "competences": "",
            "texte_brut": ""
        }
        st.session_state.cv_parsed_name = None

    prefill = st.session_state.cv_prefill

    st.markdown("---")
    st.subheader("Formulaire de candidature")

    with st.form("form_candidat"):
        nom = st.text_input("Nom complet *", value=prefill["nom"])
        email = st.text_input("Email *", value=prefill["email"])
        telephone = st.text_input("Téléphone", value=prefill["telephone"])
        pays = st.text_input("Pays")
        github = st.text_input("GitHub", value=prefill["github"])
        portfolio = st.text_input("Portfolio", value=prefill["portfolio"])
        motivation = st.text_area("Motivation / Lettre de motivation")
        competences = st.text_area(
            "Compétences (séparées par des virgules)",
            value=prefill["competences"]
        )
        experience = st.number_input(
            "Années d'expérience",
            min_value=0, max_value=50,
            value=int(prefill["experience"]) if prefill["experience"] else 0
        )
        disponibilite = st.selectbox(
            "Disponibilité", ["Immédiate", "1 mois", "3 mois", "6 mois", "Plus"]
        )
        submit = st.form_submit_button("Ajouter")

        if submit:
            if not nom or not email:
                st.error("Le nom et l'email sont obligatoires.")
            else:
                success, msg = ajouter_candidat(
                    nom, email, telephone, pays, github, portfolio,
                    motivation, competences, int(experience), disponibilite
                )
                if success:
                    st.success(msg)
                    st.session_state.cv_prefill = {
                        "nom": "", "email": "", "telephone": "",
                        "github": "", "portfolio": "",
                        "experience": 0, "competences": "",
                        "texte_brut": ""
                    }
                    st.session_state.cv_parsed_name = None
                else:
                    st.error(msg)


# ============================================================
# ÉVALUER UN CANDIDAT
# ============================================================
elif choix == "Évaluer un candidat":
    st.header("Évaluer un candidat")
    df_candidats = get_candidats()

    if df_candidats.empty:
        st.warning("Aucun candidat pour le moment.")
    else:
        df_candidats['label'] = df_candidats['nom'] + " (" + df_candidats['email'] + ")"
        selected = st.selectbox("Sélectionnez un candidat", df_candidats['label'].tolist())

        row = df_candidats[df_candidats['label'] == selected].iloc[0]
        candidat_id = int(row['id'])

        eval_exist = get_evaluation(candidat_id)

        if not eval_exist.empty:
            r = eval_exist.iloc[0]
            defaults = {
                'score_tech': int(r['score_tech']),
                'score_projet': int(r['score_projet']),
                'score_motivation': int(r['score_motivation']),
                'score_communication': int(r['score_communication']),
                'score_disponibilite': int(r['score_disponibilite']),
                'commentaire': r['commentaire'] if r['commentaire'] else ''
            }
            st.info("🔁 Évaluation existante rechargée. Ajustez si besoin.")
        else:
            candidat_data = {
                "competences": row["competences"] if row["competences"] else "",
                "experience": int(row["experience"]) if row["experience"] else 0,
                "disponibilite": row["disponibilite"] if row["disponibilite"] else ""
            }
            suggestions = proposer_scores(candidat_data)
            defaults = {
                **suggestions,
                'commentaire': ''
            }
            st.info(
                "💡 Scores pré-remplis par auto-qualification "
                "(compétences, expérience, disponibilité). "
                "Ajustez librement les curseurs."
            )

        with st.form("form_eval"):
            st.subheader("Critères d'évaluation (0-100)")
            score_tech = st.slider(
                "Compétences techniques", 0, 100, defaults['score_tech']
            )
            score_projet = st.slider(
                "Expérience projet", 0, 100, defaults['score_projet']
            )
            score_motivation = st.slider(
                "Motivation / Adéquation", 0, 100, defaults['score_motivation']
            )
            score_communication = st.slider(
                "Communication / Documentation", 0, 100, defaults['score_communication']
            )
            score_disponibilite = st.slider(
                "Disponibilité / Engagement", 0, 100, defaults['score_disponibilite']
            )
            commentaire = st.text_area("Commentaire", value=defaults['commentaire'])
            submit_eval = st.form_submit_button("Enregistrer l'évaluation")

            if submit_eval:
                scores = {
                    'score_tech': score_tech,
                    'score_projet': score_projet,
                    'score_motivation': score_motivation,
                    'score_communication': score_communication,
                    'score_disponibilite': score_disponibilite
                }
                total, priorite = enregistrer_evaluation(
                    candidat_id, scores, commentaire
                )
                st.success(
                    f"Évaluation enregistrée. "
                    f"Score total : {total}/100. Priorité : {priorite}"
                )


# ============================================================
# CLASSEMENT & PRIORITÉS
# ============================================================
elif choix == "Classement & Priorités":
    st.header("Classement & Priorités")
    df = get_classement()

    if df.empty:
        st.warning("Aucune donnée.")
    else:
        df_evalues = df[df['score_total'].notna()].copy()
        if df_evalues.empty:
            st.info("Aucun candidat évalué pour le moment.")
        else:
            df_evalues = df_evalues.sort_values('score_total', ascending=False)

            st.subheader("Classement complet")
            st.dataframe(
                df_evalues[[
                    'nom', 'email', 'pays', 'competences', 'experience',
                    'score_total', 'priorite', 'commentaire'
                ]],
                use_container_width=True
            )

            st.subheader("Profils à examiner en priorité")
            priorite_haute = df_evalues[df_evalues['priorite'] == 'Haute']
            if not priorite_haute.empty:
                st.success(f"{len(priorite_haute)} candidat(s) en priorité HAUTE")
                st.dataframe(
                    priorite_haute[['nom', 'email', 'score_total', 'commentaire']],
                    use_container_width=True
                )
            else:
                st.info("Aucun candidat en priorité haute pour le moment.")


# ============================================================
# GÉRER LES CANDIDATS
# ============================================================
elif choix == "Gérer les candidats":
    st.header("Gérer les candidats")

    df = get_candidats()
    if df.empty:
        st.info("Aucun candidat enregistré.")
    else:
        st.subheader("🗑️ Supprimer un candidat")
        df["label"] = df["nom"] + " (" + df["email"] + ")"
        selected = st.selectbox(
            "Sélectionnez le candidat à supprimer",
            df["label"].tolist(),
            key="delete_select"
        )
        candidat_id = int(df[df["label"] == selected].iloc[0]["id"])

        st.warning(
            f"⚠️ Vous êtes sur le point de supprimer **{selected}** "
            "et son évaluation. Cette action est irréversible."
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🗑️ Confirmer la suppression", type="primary"):
                supprimer_candidat(candidat_id)
                st.success(f"Candidat supprimé : {selected}")
                st.rerun()

        st.markdown("---")
        st.subheader("⚠️ Actions globales")
        st.caption(
            "Ces actions effacent des données. Utilisez-les avec précaution."
        )

        col3, col4 = st.columns(2)
        with col3:
            if st.button("Réinitialiser les évaluations"):
                reinitialiser_evaluations()
                st.success("Toutes les évaluations ont été effacées.")
                st.rerun()

        with col4:
            if st.button("🚨 Tout effacer (candidats + évaluations)"):
                reinitialiser_tout()
                st.success("Base de données vidée.")
                st.rerun()