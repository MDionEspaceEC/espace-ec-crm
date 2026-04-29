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


def get_organisation_by_id(org_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM organisations WHERE id = ?",
        conn,
        params=(org_id,)
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]


def ajouter_organisation(nom, type_org, ville, telephone, courriel, statut, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO organisations (nom, type_org, ville, telephone, courriel, statut, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, type_org, ville, telephone, courriel, statut, notes))
    conn.commit()
    conn.close()


def modifier_organisation(org_id, nom, type_org, ville, telephone, courriel, statut, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE organisations
        SET nom = ?, type_org = ?, ville = ?, telephone = ?, courriel = ?, statut = ?, notes = ?
        WHERE id = ?
    """, (nom, type_org, ville, telephone, courriel, statut, notes, org_id))
    conn.commit()
    conn.close()


def supprimer_organisation(org_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM suivis WHERE organisation_id = ?", (org_id,))
    cur.execute("DELETE FROM organisations WHERE id = ?", (org_id,))
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


def get_suivis_by_organisation(org_id):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            id,
            date_suivi,
            type_suivi,
            resume,
            prochaine_action
        FROM suivis
        WHERE organisation_id = ?
        ORDER BY date_suivi DESC, id DESC
    """, conn, params=(org_id,))
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

if "org_selectionnee" not in st.session_state:
    st.session_state.org_selectionnee = None

st.title("Espace EC CRM")
st.caption("Base interne simple pour la gestion des organismes et des suivis.")

menu = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Organismes", "Fiche organisme", "Suivis"]
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

        options = {
            f"{row['nom']} (ID {row['id']})": row["id"]
            for _, row in orgs.iterrows()
        }

        selection = st.selectbox(
            "Choisir un organisme pour ouvrir sa fiche",
            [""] + list(options.keys())
        )

        if st.button("Ouvrir la fiche"):
            if selection:
                st.session_state.org_selectionnee = options[selection]
                st.session_state.menu_force = "Fiche organisme"
                st.rerun()

elif menu == "Fiche organisme":
    orgs = get_organisations()

    if orgs.empty:
        st.info("Aucun organisme disponible.")
    else:
        options = {
            f"{row['nom']} (ID {row['id']})": row["id"]
            for _, row in orgs.iterrows()
        }

        labels = list(options.keys())
        default_index = 0

        if st.session_state.org_selectionnee in options.values():
            current_label = [k for k, v in options.items() if v == st.session_state.org_selectionnee][0]
            default_index = labels.index(current_label)

        selection = st.selectbox(
            "Sélectionner un organisme",
            labels,
            index=default_index,
            key="fiche_org_selectbox"
        )

        st.session_state.org_selectionnee = options[selection]
        org_id = st.session_state.org_selectionnee
        org = get_organisation_by_id(org_id)

        if org is None:
            st.error("Organisme introuvable.")
        else:
            st.subheader(f"Fiche de : {org['nom']}")

            col1, col2, col3 = st.columns(3)
            col1.metric("ID", int(org["id"]))
            col2.metric("Ville", org["ville"] if org["ville"] else "-")
            col3.metric("Statut", org["statut"] if org["statut"] else "-")

            st.markdown("### Informations")
            info1, info2 = st.columns(2)

            with info1:
                st.write(f"**Type** : {org['type_org'] if org['type_org'] else '-'}")
                st.write(f"**Téléphone** : {org['telephone'] if org['telephone'] else '-'}")

            with info2:
                st.write(f"**Courriel** : {org['courriel'] if org['courriel'] else '-'}")
                st.write(f"**Notes** : {org['notes'] if org['notes'] else '-'}")

            st.markdown("### Modifier l'organisme")

            types_disponibles = ["", "OBNL", "Coopérative", "Entreprise d'économie sociale", "Institution", "Autre"]
            statuts_disponibles = ["Actif", "En démarrage", "À relancer", "Inactif"]

            with st.form("form_modifier_organisation"):
                col1, col2 = st.columns(2)

                with col1:
                    nom_mod = st.text_input("Nom de l'organisme *", value=org["nom"])
                    type_mod = st.selectbox(
                        "Type d'organisme",
                        types_disponibles,
                        index=types_disponibles.index(org["type_org"]) if org["type_org"] in types_disponibles else 0
                    )
                    ville_mod = st.text_input("Ville", value=org["ville"] if org["ville"] else "")
                    telephone_mod = st.text_input("Téléphone", value=org["telephone"] if org["telephone"] else "")

                with col2:
                    courriel_mod = st.text_input("Courriel", value=org["courriel"] if org["courriel"] else "")
                    statut_mod = st.selectbox(
                        "Statut",
                        statuts_disponibles,
                        index=statuts_disponibles.index(org["statut"]) if org["statut"] in statuts_disponibles else 0
                    )
                    notes_mod = st.text_area("Notes", value=org["notes"] if org["notes"] else "")

                submit_mod = st.form_submit_button("Enregistrer les modifications")

                if submit_mod:
                    if not nom_mod.strip():
                        st.error("Le nom de l'organisme est obligatoire.")
                    else:
                        modifier_organisation(
                            org_id,
                            nom_mod.strip(),
                            type_mod,
                            ville_mod.strip(),
                            telephone_mod.strip(),
                            courriel_mod.strip(),
                            statut_mod,
                            notes_mod.strip()
                        )
                        st.success("Organisme modifié avec succès.")
                        st.rerun()

            st.markdown("### Suivis liés")
            suivis_org = get_suivis_by_organisation(org_id)

            if suivis_org.empty:
                st.info("Aucun suivi pour cet organisme.")
            else:
                st.dataframe(suivis_org, use_container_width=True)

            st.markdown("### Suppression")
            confirmation = st.checkbox("Je confirme la suppression de cet organisme et de ses suivis liés.")
            if st.button("Supprimer cet organisme", type="secondary"):
                if confirmation:
                    supprimer_organisation(org_id)
                    st.session_state.org_selectionnee = None
                    st.success("Organisme supprimé avec succès.")
                    st.rerun()
                else:
                    st.warning("Tu dois confirmer la suppression avant de continuer.")

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
            type_suivi = st.selectbox(
                "Type de suivi",
                ["Téléphone", "Courriel", "Rencontre", "Visite", "Autre"]
            )
            resume = st.text_area("Résumé du suivi *")
            prochaine_action = st.text_area("Prochaine action")

            submit_suivi = st.form_submit_button("Enregistrer le suivi")

            if submit_suivi:
                if not resume.strip():
                    st.error("Le résumé du suivi est obligatoire.")
                else:
                    ajouter_suivi(
                        options_orgs[organisation_label],
                        str(date_suivi),
                        type_suivi,
                        resume.strip(),
                        prochaine_action.strip()
                    )
                    st.success("Suivi ajouté avec succès.")
                    st.rerun()

    st.subheader("Historique des suivis")
    suivis = get_suivis()

    if suivis.empty:
        st.info("Aucun suivi enregistré.")
    else:
        st.dataframe(suivis, use_container_width=True)
