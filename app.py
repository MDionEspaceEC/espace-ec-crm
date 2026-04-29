import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Espace EC CRM",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "espace_ec_crm.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS organisations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            type_org TEXT,
            ville TEXT,
            telephone TEXT,
            courriel TEXT,
            statut TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS suivis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organisation_id INTEGER NOT NULL,
            date_suivi TEXT NOT NULL,
            type_suivi TEXT,
            resume TEXT,
            prochaine_action TEXT,
            FOREIGN KEY (organisation_id) REFERENCES organisations (id)
        )
    """)

    conn.commit()
    conn.close()


def get_organisations():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM organisations ORDER BY nom ASC",
        conn
    )
    conn.close()
    return df


def ajouter_organisation(nom, type_org, ville, telephone, courriel, statut, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO organisations (nom, type_org, ville, telephone, courriel, statut, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, type_org, ville, telephone, courriel, statut, notes))
    conn.commit()
    conn.close()


def get_suivis():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            suivis.id,
            suivis.date_suivi,
            suivis.type_suivi,
            organisations.nom AS organisation,
            suivis.resume,
            suivis.prochaine_action
        FROM suivis
        JOIN organisations ON suivis.organisation_id = organisations.id
        ORDER BY suivis.date_suivi DESC, suivis.id DESC
    """, conn)
    conn.close()
    return df


def ajouter_suivi(organisation_id, date_suivi, type_suivi, resume, prochaine_action):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO suivis (organisation_id, date_suivi, type_suivi, resume, prochaine_action)
        VALUES (?, ?, ?, ?, ?)
    """, (organisation_id, date_suivi, type_suivi, resume, prochaine_action))
    conn.commit()
    conn.close()


init_db()

st.title("Espace EC CRM")
st.caption("Base interne simple pour la gestion des organismes et des suivis.")

menu = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Organismes", "Suivis"]
)

if menu == "Tableau de bord":
    orgs = get_organisations()
    suivis = get_suivis()

    col1, col2 = st.columns(2)
    col1.metric("Nombre d'organismes", len(orgs))
    col2.metric("Nombre de suivis", len(suivis))

    st.subheader("Derniers suivis")
    if suivis.empty:
        st.info("Aucun suivi enregistré pour le moment.")
    else:
        st.dataframe(suivis.head(10), use_container_width=True)

elif menu == "Organismes":
    st.subheader("Ajouter un organisme")

    with st.form("form_organisation", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom de l'organisme *")
            type_org = st.selectbox(
                "Type d'organisme",
                ["", "OBNL", "Coopérative", "Entreprise d'économie sociale", "Institution", "Autre"]
            )
            ville = st.text_input("Ville")
            telephone = st.text_input("Téléphone")

        with col2:
            courriel = st.text_input("Courriel")
            statut = st.selectbox(
                "Statut",
                ["Actif", "En démarrage", "À relancer", "Inactif"]
            )
            notes = st.text_area("Notes")

        submit_org = st.form_submit_button("Enregistrer l'organisme")

        if submit_org:
            if not nom.strip():
                st.error("Le nom de l'organisme est obligatoire.")
            else:
                ajouter_organisation(
                    nom.strip(),
                    type_org,
                    ville.strip(),
                    telephone.strip(),
                    courriel.strip(),
                    statut,
                    notes.strip()
                )
                st.success("Organisme ajouté avec succès.")
                st.rerun()

    st.subheader("Liste des organismes")
    orgs = get_organisations()

    if orgs.empty:
        st.info("Aucun organisme enregistré.")
    else:
        recherche = st.text_input("Rechercher un organisme par nom")
        if recherche:
            orgs = orgs[orgs["nom"].str.contains(recherche, case=False, na=False)]
        st.dataframe(orgs, use_container_width=True)

elif menu == "Suivis":
    st.subheader("Ajouter un suivi")

    orgs = get_organisations()

    if orgs.empty:
        st.warning("Ajoute d'abord un organisme avant de créer un suivi.")
    else:
        options_orgs = {
            f"{row['nom']} ({row['ville']})" if row['ville'] else row['nom']: row["id"]
            for _, row in orgs.iterrows()
        }

        with st.form("form_suivi", clear_on_submit=True):
            organisation_label = st.selectbox(
                "Organisme",
                list(options_orgs.keys())
            )
            date_suivi = st.date_input("Date du suivi", value=date.today())
            type_sui
