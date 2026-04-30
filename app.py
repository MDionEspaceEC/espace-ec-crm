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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organisation_id INTEGER NOT NULL,
            nom TEXT NOT NULL,
            role TEXT,
            telephone TEXT,
            courriel TEXT,
            notes TEXT,
            FOREIGN KEY (organisation_id) REFERENCES organisations (id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS taches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organisation_id INTEGER,
            titre TEXT NOT NULL,
            responsable TEXT,
            echeance TEXT,
            statut TEXT,
            priorite TEXT,
            notes TEXT,
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
    cur.execute("DELETE FROM contacts WHERE organisation_id = ?", (org_id,))
    cur.execute("DELETE FROM taches WHERE organisation_id = ?", (org_id,))
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


def get_contacts_by_organisation(org_id):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            id,
            nom,
            role,
            telephone,
            courriel,
            notes
        FROM contacts
        WHERE organisation_id = ?
        ORDER BY nom ASC
    """, conn, params=(org_id,))
    conn.close()
    return df


def get_contact_by_id(contact_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM contacts WHERE id = ?",
        conn,
        params=(contact_id,)
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]


def ajouter_contact(organisation_id, nom, role, telephone, courriel, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contacts (organisation_id, nom, role, telephone, courriel, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (organisation_id, nom, role, telephone, courriel, notes))
    conn.commit()
    conn.close()


def modifier_contact(contact_id, nom, role, telephone, courriel, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE contacts
        SET nom = ?, role = ?, telephone = ?, courriel = ?, notes = ?
        WHERE id = ?
    """, (nom, role, telephone, courriel, notes, contact_id))
    conn.commit()
    conn.close()


def supprimer_contact(contact_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()


def get_taches():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            taches.id,
            taches.titre,
            COALESCE(organisations.nom, '-') AS organisation,
            taches.responsable,
            taches.echeance,
            taches.statut,
            taches.priorite,
            taches.notes
        FROM taches
        LEFT JOIN organisations ON taches.organisation_id = organisations.id
        ORDER BY
            CASE
                WHEN taches.statut = 'À faire' THEN 1
                WHEN taches.statut = 'En cours' THEN 2
                WHEN taches.statut = 'Terminée' THEN 3
                ELSE 4
            END,
            taches.echeance ASC,
            taches.id DESC
    """, conn)
    conn.close()
    return df


def get_taches_by_organisation(org_id):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            id,
            titre,
            responsable,
            echeance,
            statut,
            priorite,
            notes
        FROM taches
        WHERE organisation_id = ?
        ORDER BY echeance ASC, id DESC
    """, conn, params=(org_id,))
    conn.close()
    return df


def get_tache_by_id(tache_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM taches WHERE id = ?",
        conn,
        params=(tache_id,)
    )
    conn.close()
    if df.empty:
        return None
    return df.iloc[0]


def ajouter_tache(organisation_id, titre, responsable, echeance, statut, priorite, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO taches (organisation_id, titre, responsable, echeance, statut, priorite, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (organisation_id, titre, responsable, echeance, statut, priorite, notes))
    conn.commit()
    conn.close()


def modifier_tache(tache_id, organisation_id, titre, responsable, echeance, statut, priorite, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE taches
        SET organisation_id = ?, titre = ?, responsable = ?, echeance = ?, statut = ?, priorite = ?, notes = ?
        WHERE id = ?
    """, (organisation_id, titre, responsable, echeance, statut, priorite, notes, tache_id))
    conn.commit()
    conn.close()


def supprimer_tache(tache_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM taches WHERE id = ?", (tache_id,))
    conn.commit()
    conn.close()


init_db()

if "org_selectionnee" not in st.session_state:
    st.session_state.org_selectionnee = None

st.title("Espace EC CRM")
st.caption("Base interne simple pour la gestion des organismes, suivis, contacts et tâches.")

menu = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Organismes", "Fiche organisme", "Suivis", "Tâches"]
)

if menu == "Tableau de bord":
    orgs = get_organisations()
    suivis = get_suivis()
    taches = get_taches()

    col1, col2, col3 = st.columns(3)
    col1.metric("Organismes", len(orgs))
    col2.metric("Suivis", len(suivis))
    col3.metric("Tâches", len(taches))

    st.subheader("Derniers suivis")
    if suivis.empty:
        st.info("Aucun suivi enregistré pour le moment.")
    else:
        st.dataframe(suivis.head(8), use_container_width=True)

    st.subheader("Tâches en cours")
    if taches.empty:
        st.info("Aucune tâche enregistrée.")
    else:
        taches_actives = taches[taches["statut"].isin(["À faire", "En cours"])]
        st.dataframe(taches_actives.head(8), use_container_width=True)

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

            st.markdown("### Contacts liés")
            contacts_org = get_contacts_by_organisation(org_id)

            with st.form("form_contact", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    contact_nom = st.text_input("Nom du contact *")
                    contact_role = st.text_input("Rôle / fonction")
                    contact_telephone = st.text_input("Téléphone")
                with c2:
                    contact_courriel = st.text_input("Courriel")
                    contact_notes = st.text_area("Notes contact")

                submit_contact = st.form_submit_button("Ajouter le contact")

                if submit_contact:
                    if not contact_nom.strip():
                        st.error("Le nom du contact est obligatoire.")
                    else:
                        ajouter_contact(
                            org_id,
                            contact_nom.strip(),
                            contact_role.strip(),
                            contact_telephone.strip(),
                            contact_courriel.strip(),
                            contact_notes.strip()
                        )
                        st.success("Contact ajouté avec succès.")
                        st.rerun()

            if contacts_org.empty:
                st.info("Aucun contact pour cet organisme.")
            else:
                st.dataframe(contacts_org, use_container_width=True)

                contacts_options = {
                    f"{row['nom']} (ID {row['id']})": row["id"]
                    for _, row in contacts_org.iterrows()
                }

                contact_selection = st.selectbox(
                    "Choisir un contact à modifier ou supprimer",
                    list(contacts_options.keys()),
                    key="contact_selection"
                )

                contact_id = contacts_options[contact_selection]
                contact = get_contact_by_id(contact_id)

                if contact is not None:
                    with st.form("form_modifier_contact"):
                        mc1, mc2 = st.columns(2)

                        with mc1:
                            nom_c_mod = st.text_input("Nom du contact *", value=contact["nom"])
                            role_c_mod = st.text_input("Rôle / fonction", value=contact["role"] if contact["role"] else "")
                            tel_c_mod = st.text_input("Téléphone", value=contact["telephone"] if contact["telephone"] else "")

                        with mc2:
                            courriel_c_mod = st.text_input("Courriel", value=contact["courriel"] if contact["courriel"] else "")
                            notes_c_mod = st.text_area("Notes", value=contact["notes"] if contact["notes"] else "")

                        submit_mod_contact = st.form_submit_button("Enregistrer les modifications du contact")

                        if submit_mod_contact:
                            if not nom_c_mod.strip():
                                st.error("Le nom du contact est obligatoire.")
                            else:
                                modifier_contact(
                                    contact_id,
                                    nom_c_mod.strip(),
                                    role_c_mod.strip(),
                                    tel_c_mod.strip(),
                                    courriel_c_mod.strip(),
                                    notes_c_mod.strip()
                                )
                                st.success("Contact modifié avec succès.")
                                st.rerun()

                    confirm_delete_contact = st.checkbox(
                        "Je confirme la suppression de ce contact.",
                        key=f"delete_contact_{contact_id}"
                    )
                    if st.button("Supprimer ce contact", key=f"btn_delete_contact_{contact_id}"):
                        if confirm_delete_contact:
                            supprimer_contact(contact_id)
                            st.success("Contact supprimé avec succès.")
                            st.rerun()
                        else:
                            st.warning("Tu dois confirmer la suppression du contact.")

            st.markdown("### Suivis liés")
            suivis_org = get_suivis_by_organisation(org_id)

            if suivis_org.empty:
                st.info("Aucun suivi pour cet organisme.")
            else:
                st.dataframe(suivis_org, use_container_width=True)

            st.markdown("### Tâches liées")
            taches_org = get_taches_by_organisation(org_id)

            with st.form("form_tache_fiche", clear_on_submit=True):
                t1, t2 = st.columns(2)
                with t1:
                    tache_titre = st.text_input("Titre de la tâche *")
                    tache_responsable = st.text_input("Responsable")
                    tache_echeance = st.date_input("Échéance", value=date.today(), key="echeance_fiche")
                with t2:
                    tache_statut = st.selectbox("Statut", ["À faire", "En cours", "Terminée"], key="statut_fiche")
                    tache_priorite = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute"], key="priorite_fiche")
                    tache_notes = st.text_area("Notes de la tâche", key="notes_fiche")

                submit_tache = st.form_submit_button("Ajouter la tâche")

                if submit_tache:
                    if not tache_titre.strip():
                        st.error("Le titre de la tâche est obligatoire.")
                    else:
                        ajouter_tache(
                            org_id,
                            tache_titre.strip(),
                            tache_responsable.strip(),
                            str(tache_echeance),
                            tache_statut,
                            tache_priorite,
                            tache_notes.strip()
                        )
                        st.success("Tâche ajoutée avec succès.")
                        st.rerun()

            if taches_org.empty:
                st.info("Aucune tâche liée à cet organisme.")
            else:
                st.dataframe(taches_org, use_container_width=True)

                taches_options = {
                    f"{row['titre']} (ID {row['id']})": row["id"]
                    for _, row in taches_org.iterrows()
                }

                tache_selection = st.selectbox(
                    "Choisir une tâche à modifier ou supprimer",
                    list(taches_options.keys()),
                    key="tache_selection_fiche"
                )

                tache_id = taches_options[tache_selection]
                tache = get_tache_by_id(tache_id)

                if tache is not None:
                    with st.form("form_modifier_tache_fiche"):
                        mt1, mt2 = st.columns(2)

                        with mt1:
                            titre_t_mod = st.text_input("Titre de la tâche *", value=tache["titre"])
                            responsable_t_mod = st.text_input("Responsable", value=tache["responsable"] if tache["responsable"] else "")
                            echeance_value = pd.to_datetime(tache["echeance"]).date() if tache["echeance"] else date.today()
                            echeance_t_mod = st.date_input("Échéance", value=echeance_value, key=f"edit_echeance_{tache_id}")

                        with mt2:
                            statuts = ["À faire", "En cours", "Terminée"]
                            priorites = ["Basse", "Moyenne", "Haute"]

                            statut_t_mod = st.selectbox(
                                "Statut",
                                statuts,
                                index=statuts.index(tache["statut"]) if tache["statut"] in statuts else 0,
                                key=f"edit_statut_{tache_id}"
                            )
                            priorite_t_mod = st.selectbox(
                                "Priorité",
                                priorites,
                                index=priorites.index(tache["priorite"]) if tache["priorite"] in priorites else 1,
                                key=f"edit_priorite_{tache_id}"
                            )
                            notes_t_mod = st.text_area("Notes", value=tache["notes"] if tache["notes"] else "", key=f"edit_notes_{tache_id}")

                        submit_mod_tache = st.form_submit_button("Enregistrer les modifications de la tâche")

                        if submit_mod_tache:
                            if not titre_t_mod.strip():
                                st.error("Le titre de la tâche est obligatoire.")
                            else:
                                modifier_tache(
                                    tache_id,
                                    org_id,
                                    titre_t_mod.strip(),
                                    responsable_t_mod.strip(),
                                    str(echeance_t_mod),
                                    statut_t_mod,
                                    priorite_t_mod,
                                    notes_t_mod.strip()
                                )
                                st.success("Tâche modifiée avec succès.")
                                st.rerun()

                    confirm_delete_tache = st.checkbox(
                        "Je confirme la suppression de cette tâche.",
                        key=f"delete_tache_{tache_id}"
                    )
                    if st.button("Supprimer cette tâche", key=f"btn_delete_tache_{tache_id}"):
                        if confirm_delete_tache:
                            supprimer_tache(tache_id)
                            st.success("Tâche supprimée avec succès.")
                            st.rerun()
                        else:
                            st.warning("Tu dois confirmer la suppression de la tâche.")

            st.markdown("### Suppression")
            confirmation = st.checkbox("Je confirme la suppression de cet organisme et de ses éléments liés.")
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
            organisation_label = st.selectbox("Organisme", list(options_orgs.keys()))
            date_suivi = st.date_input("Date du suivi", value=date.today())
            type_suivi = st.selectbox("Type de suivi", ["Téléphone", "Courriel", "Rencontre", "Visite", "Autre"])
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

elif menu == "Tâches":
    st.subheader("Ajouter une tâche")

    orgs = get_organisations()
    options_orgs = {"Aucun organisme lié": None}

    if not orgs.empty:
        for _, row in orgs.iterrows():
            label = f"{row['nom']} ({row['ville']})" if row['ville'] else row['nom']
            options_orgs[label] = row["id"]

    with st.form("form_tache_generale", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            titre = st.text_input("Titre de la tâche *")
            org_label = st.selectbox("Organisme lié", list(options_orgs.keys()))
            responsable = st.text_input("Responsable")
            echeance = st.date_input("Échéance", value=date.today(), key="echeance_generale")

        with col2:
            statut = st.selectbox("Statut", ["À faire", "En cours", "Terminée"], key="statut_general")
            priorite = st.selectbox("Priorité", ["Basse", "Moyenne", "Haute"], key="priorite_generale")
            notes = st.text_area("Notes")

        submit_tache_generale = st.form_submit_button("Enregistrer la tâche")

        if submit_tache_generale:
            if not titre.strip():
                st.error("Le titre de la tâche est obligatoire.")
            else:
                ajouter_tache(
                    options_orgs[org_label],
                    titre.strip(),
                    responsable.strip(),
                    str(echeance),
                    statut,
                    priorite,
                    notes.strip()
                )
                st.success("Tâche ajoutée avec succès.")
                st.rerun()

    st.subheader("Liste des tâches")
    taches = get_taches()

    if taches.empty:
        st.info("Aucune tâche enregistrée.")
    else:
        filtre_statut = st.selectbox(
            "Filtrer par statut",
            ["Toutes", "À faire", "En cours", "Terminée"]
        )

        if filtre_statut != "Toutes":
            taches = taches[taches["statut"] == filtre_statut]

        st.dataframe(taches, use_container_width=True)

        taches_options_global = {
            f"{row['titre']} (ID {row['id']})": row["id"]
            for _, row in taches.iterrows()
        }

        tache_selection_global = st.selectbox(
            "Choisir une tâche à modifier ou supprimer",
            list(taches_options_global.keys()),
            key="tache_selection_global"
        )

        tache_id_global = taches_options_global[tache_selection_global]
        tache_global = get_tache_by_id(tache_id_global)

        if tache_global is not None:
            orgs_for_edit = get_organisations()
            org_options_edit = {"Aucun organisme lié": None}
            for _, row in orgs_for_edit.iterrows():
                org_options_edit[f"{row['nom']} (ID {row['id']})"] = row["id"]

            org_labels_edit = list(org_options_edit.keys())
            current_org_label = "Aucun organisme lié"
            for label, value in org_options_edit.items():
                if value == tache_global["organisation_id"]:
                    current_org_label = label
                    break

            with st.form("form_modifier_tache_global"):
                gt1, gt2 = st.columns(2)

                with gt1:
                    titre_g_mod = st.text_input("Titre de la tâche *", value=tache_global["titre"])
                    org_g_mod = st.selectbox(
                        "Organisme lié",
                        org_labels_edit,
                        index=org_labels_edit.index(current_org_label)
                    )
                    responsable_g_mod = st.text_input("Responsable", value=tache_global["responsable"] if tache_global["responsable"] else "")
                    echeance_g_value = pd.to_datetime(tache_global["echeance"]).date() if tache_global["echeance"] else date.today()
                    echeance_g_mod = st.date_input("Échéance", value=echeance_g_value, key=f"global_echeance_{tache_id_global}")

                with gt2:
                    statuts = ["À faire", "En cours", "Terminée"]
                    priorites = ["Basse", "Moyenne", "Haute"]

                    statut_g_mod = st.selectbox(
                        "Statut",
                        statuts,
                        index=statuts.index(tache_global["statut"]) if tache_global["statut"] in statuts else 0,
                        key=f"global_statut_{tache_id_global}"
                    )
                    priorite_g_mod = st.selectbox(
                        "Priorité",
                        priorites,
                        index=priorites.index(tache_global["priorite"]) if tache_global["priorite"] in priorites else 1,
                        key=f"global_priorite_{tache_id_global}"
                    )
                    notes_g_mod = st.text_area("Notes", value=tache_global["notes"] if tache_global["notes"] else "", key=f"global_notes_{tache_id_global}")

                submit_mod_tache_global = st.form_submit_button("Enregistrer les modifications de la tâche")

                if submit_mod_tache_global:
                    if not titre_g_mod.strip():
                        st.error("Le titre de la tâche est obligatoire.")
                    else:
                        modifier_tache(
                            tache_id_global,
                            org_options_edit[org_g_mod],
                            titre_g_mod.strip(),
                            responsable_g_mod.strip(),
                            str(echeance_g_mod),
                            statut_g_mod,
                            priorite_g_mod,
                            notes_g_mod.strip()
                        )
                        st.success("Tâche modifiée avec succès.")
                        st.rerun()

            confirm_delete_tache_global = st.checkbox(
                "Je confirme la suppression de cette tâche.",
                key=f"delete_tache_global_{tache_id_global}"
            )
            if st.button("Supprimer cette tâche", key=f"btn_delete_tache_global_{tache_id_global}"):
                if confirm_delete_tache_global:
                    supprimer_tache(tache_id_global)
                    st.success("Tâche supprimée avec succès.")
                    st.rerun()
                else:
                    st.warning("Tu dois confirmer la suppression de la tâche.")
