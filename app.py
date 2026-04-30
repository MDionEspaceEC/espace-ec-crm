
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="Espace EC CRM",
    page_icon="ðŸ“‹",
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

    cur.execute("PRAGMA table_info(organisations)")
    colonnes_org = [row[1] for row in cur.fetchall()]
    if "employe_id_attitre" not in colonnes_org:
        cur.execute("ALTER TABLE organisations ADD COLUMN employe_id_attitre INTEGER")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            poste TEXT,
            courriel TEXT,
            telephone TEXT,
            statut_emploi TEXT,
            heures_semaine REAL,
            actif TEXT
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
            employe_id INTEGER,
            titre TEXT NOT NULL,
            responsable TEXT,
            echeance TEXT,
            statut TEXT,
            priorite TEXT,
            notes TEXT,
            FOREIGN KEY (organisation_id) REFERENCES organisations (id),
            FOREIGN KEY (employe_id) REFERENCES employes (id)
        )
    """)

    conn.commit()
    conn.close()


def get_organisations():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM organisations ORDER BY nom ASC", conn)
    conn.close()
    return df


def get_organisation_by_id(org_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM organisations WHERE id = ?", conn, params=(org_id,))
    conn.close()
    return None if df.empty else df.iloc[0]


def ajouter_organisation(nom, type_org, ville, telephone, courriel, statut, notes, employe_id_attitre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO organisations (nom, type_org, ville, telephone, courriel, statut, notes, employe_id_attitre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nom, type_org, ville, telephone, courriel, statut, notes, employe_id_attitre))
    conn.commit()
    conn.close()


def modifier_organisation(org_id, nom, type_org, ville, telephone, courriel, statut, notes, employe_id_attitre):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE organisations
        SET nom = ?, type_org = ?, ville = ?, telephone = ?, courriel = ?, statut = ?, notes = ?, employe_id_attitre = ?
        WHERE id = ?
    """, (nom, type_org, ville, telephone, courriel, statut, notes, employe_id_attitre, org_id))
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


def get_employes():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM employes ORDER BY nom ASC", conn)
    conn.close()
    return df


def get_employe_by_id(employe_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM employes WHERE id = ?", conn, params=(employe_id,))
    conn.close()
    return None if df.empty else df.iloc[0]


def ajouter_employe(nom, poste, courriel, telephone, statut_emploi, heures_semaine, actif):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO employes (nom, poste, courriel, telephone, statut_emploi, heures_semaine, actif)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, poste, courriel, telephone, statut_emploi, heures_semaine, actif))
    conn.commit()
    conn.close()


def modifier_employe(employe_id, nom, poste, courriel, telephone, statut_emploi, heures_semaine, actif):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE employes
        SET nom = ?, poste = ?, courriel = ?, telephone = ?, statut_emploi = ?, heures_semaine = ?, actif = ?
        WHERE id = ?
    """, (nom, poste, courriel, telephone, statut_emploi, heures_semaine, actif, employe_id))
    conn.commit()
    conn.close()


def supprimer_employe(employe_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE taches
        SET employe_id = NULL, responsable = ''
        WHERE employe_id = ?
    """, (employe_id,))
    cur.execute("""
        UPDATE organisations
        SET employe_id_attitre = NULL
        WHERE employe_id_attitre = ?
    """, (employe_id,))
    cur.execute("DELETE FROM employes WHERE id = ?", (employe_id,))
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
        SELECT id, date_suivi, type_suivi, resume, prochaine_action
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
        SELECT id, nom, role, telephone, courriel, notes
        FROM contacts
        WHERE organisation_id = ?
        ORDER BY nom ASC
    """, conn, params=(org_id,))
    conn.close()
    return df


def ajouter_contact(organisation_id, nom, role, telephone, courriel, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO contacts (organisation_id, nom, role, telephone, courriel, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (organisation_id, nom, role, telephone, courriel, notes))
    conn.commit()
    conn.close()


def get_taches():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            taches.id,
            taches.titre,
            COALESCE(organisations.nom, '-') AS organisation,
            COALESCE(employes.nom, taches.responsable, '-') AS employe_assigne,
            taches.responsable,
            taches.echeance,
            taches.statut,
            taches.priorite,
            taches.notes
        FROM taches
        LEFT JOIN organisations ON taches.organisation_id = organisations.id
        LEFT JOIN employes ON taches.employe_id = employes.id
        ORDER BY
            CASE
                WHEN taches.statut = 'Ã€ faire' THEN 1
                WHEN taches.statut = 'En cours' THEN 2
                WHEN taches.statut = 'TerminÃ©e' THEN 3
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
            notes,
            employe_id
        FROM taches
        WHERE organisation_id = ?
        ORDER BY echeance ASC, id DESC
    """, conn, params=(org_id,))
    conn.close()
    return df


def get_taches_by_employe(employe_id):
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT
            taches.id,
            taches.titre,
            COALESCE(organisations.nom, '-') AS organisation,
            taches.echeance,
            taches.statut,
            taches.priorite,
            taches.notes
        FROM taches
        LEFT JOIN organisations ON taches.organisation_id = organisations.id
        WHERE taches.employe_id = ?
        ORDER BY
            CASE
                WHEN taches.statut = 'Ã€ faire' THEN 1
                WHEN taches.statut = 'En cours' THEN 2
                WHEN taches.statut = 'TerminÃ©e' THEN 3
                ELSE 4
            END,
            taches.echeance ASC
    """, conn, params=(employe_id,))
    conn.close()
    return df


def get_tache_by_id(tache_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM taches WHERE id = ?", conn, params=(tache_id,))
    conn.close()
    return None if df.empty else df.iloc[0]


def ajouter_tache(organisation_id, employe_id, titre, responsable, echeance, statut, priorite, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO taches (organisation_id, employe_id, titre, responsable, echeance, statut, priorite, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (organisation_id, employe_id, titre, responsable, echeance, statut, priorite, notes))
    conn.commit()
    conn.close()


def modifier_tache(tache_id, organisation_id, employe_id, titre, responsable, echeance, statut, priorite, notes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE taches
        SET organisation_id = ?, employe_id = ?, titre = ?, responsable = ?, echeance = ?, statut = ?, priorite = ?, notes = ?
        WHERE id = ?
    """, (organisation_id, employe_id, titre, responsable, echeance, statut, priorite, notes, tache_id))
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
st.caption("Base interne simple pour la gestion des organismes, employÃ©s, suivis, contacts et tÃ¢ches.")

menu = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Organismes", "EmployÃ©s", "Fiche organisme", "Suivis", "TÃ¢ches"]
)

if menu == "Tableau de bord":
    orgs = get_organisations()
    employes = get_employes()
    suivis = get_suivis()
    taches = get_taches()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Organismes", len(orgs))
    c2.metric("EmployÃ©s", len(employes))
    c3.metric("Suivis", len(suivis))
    c4.metric("TÃ¢ches", len(taches))

    st.subheader("TÃ¢ches en cours")
    taches_actives = taches[taches["statut"].isin(["Ã€ faire", "En cours"])] if not taches.empty else pd.DataFrame()
    if taches_actives.empty:
        st.info("Aucune tÃ¢che active.")
    else:
        st.dataframe(taches_actives.head(10), use_container_width=True)

elif menu == "Organismes":
    st.subheader("Ajouter un organisme")

    employes = get_employes()
    options_employes = {"Aucun employÃ© attitrÃ©": None}
    for _, row in employes.iterrows():
        options_employes[f"{row['nom']} (ID {row['id']})"] = row["id"]

    with st.form("form_organisation", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            nom = st.text_input("Nom de l'organisme *")
            type_org = st.selectbox("Type d'organisme", ["", "OBNL", "CoopÃ©rative", "Entreprise d'Ã©conomie sociale", "Institution", "Autre"])
            ville = st.text_input("Ville")
            telephone = st.text_input("TÃ©lÃ©phone")

        with col2:
            courriel = st.text_input("Courriel")
            statut = st.selectbox("Statut", ["Actif", "En dÃ©marrage", "Ã€ relancer", "Inactif"])
            employe_attitre_label = st.selectbox("EmployÃ© attitrÃ© Ã  l'organisme", list(options_employes.keys()))
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
                    notes.strip(),
                    options_employes[employe_attitre_label]
                )
                st.success("Organisme ajoutÃ© avec succÃ¨s.")
                st.rerun()

    st.subheader("Liste des organismes")
    orgs = get_organisations()

    if orgs.empty:
        st.info("Aucun organisme enregistrÃ©.")
    else:
        st.dataframe(orgs, use_container_width=True)

        options = {f"{row['nom']} (ID {row['id']})": row["id"] for _, row in orgs.iterrows()}
        selection = st.selectbox("Choisir un organisme pour ouvrir sa fiche", [""] + list(options.keys()))

        if st.button("Ouvrir la fiche"):
            if selection:
                st.session_state.org_selectionnee = options[selection]
                st.rerun()

elif menu == "EmployÃ©s":
    st.subheader("Ajouter un employÃ©")

    with st.form("form_employe", clear_on_submit=True):
        e1, e2 = st.columns(2)

        with e1:
            nom = st.text_input("Nom de l'employÃ© *")
            poste = st.text_input("Poste")
            courriel = st.text_input("Courriel")
            telephone = st.text_input("TÃ©lÃ©phone")

        with e2:
            statut_emploi = st.selectbox("Statut d'emploi", ["Temps plein", "Temps partiel", "Contractuel", "Stagiaire", "Autre"])
            heures_semaine = st.number_input("Heures par semaine", min_value=0.0, step=0.5, value=35.0)
            actif = st.selectbox("Actif", ["Oui", "Non"])

        submit_employe = st.form_submit_button("Enregistrer l'employÃ©")

        if submit_employe:
            if not nom.strip():
                st.error("Le nom de l'employÃ© est obligatoire.")
            else:
                ajouter_employe(
                    nom.strip(),
                    poste.strip(),
                    courriel.strip(),
                    telephone.strip(),
                    statut_emploi,
                    heures_semaine,
                    actif
                )
                st.success("EmployÃ© ajoutÃ© avec succÃ¨s.")
                st.rerun()

    st.subheader("Liste des employÃ©s")
    employes = get_employes()

    if employes.empty:
        st.info("Aucun employÃ© enregistrÃ©.")
    else:
        st.dataframe(employes, use_container_width=True)

        employe_options = {f"{row['nom']} (ID {row['id']})": row["id"] for _, row in employes.iterrows()}
        employe_selection = st.selectbox("Choisir un employÃ©", list(employe_options.keys()))
        employe_id = employe_options[employe_selection]
        employe = get_employe_by_id(employe_id)

        if employe is not None:
            st.markdown("### Modifier l'employÃ©")

            with st.form("form_modifier_employe"):
                me1, me2 = st.columns(2)

                with me1:
                    nom_mod = st.text_input("Nom de l'employÃ© *", value=employe["nom"])
                    poste_mod = st.text_input("Poste", value=employe["poste"] if employe["poste"] else "")
                    courriel_mod = st.text_input("Courriel", value=employe["courriel"] if employe["courriel"] else "")
                    telephone_mod = st.text_input("TÃ©lÃ©phone", value=employe["telephone"] if employe["telephone"] else "")

                with me2:
                    statuts = ["Temps plein", "Temps partiel", "Contractuel", "Stagiaire", "Autre"]
                    statut_mod = st.selectbox(
                        "Statut d'emploi",
                        statuts,
                        index=statuts.index(employe["statut_emploi"]) if employe["statut_emploi"] in statuts else 0
                    )
                    heures_mod = st.number_input("Heures par semaine", min_value=0.0, step=0.5, value=float(employe["heures_semaine"]) if employe["heures_semaine"] else 35.0)
                    actif_mod = st.selectbox("Actif", ["Oui", "Non"], index=0 if employe["actif"] == "Oui" else 1)

                submit_mod_employe = st.form_submit_button("Enregistrer les modifications")

                if submit_mod_employe:
                    if not nom_mod.strip():
                        st.error("Le nom de l'employÃ© est obligatoire.")
                    else:
                        modifier_employe(
                            employe_id,
                            nom_mod.strip(),
                            poste_mod.strip(),
                            courriel_mod.strip(),
                            telephone_mod.strip(),
                            statut_mod,
                            heures_mod,
                            actif_mod
                        )
                        st.success("EmployÃ© modifiÃ© avec succÃ¨s.")
                        st.rerun()

            st.markdown("### TÃ¢ches de l'employÃ©")
            taches_employe = get_taches_by_employe(employe_id)

            if taches_employe.empty:
                st.info("Aucune tÃ¢che assignÃ©e Ã  cet employÃ©.")
            else:
                st.dataframe(taches_employe, use_container_width=True)

            confirm_delete_employe = st.checkbox("Je confirme la suppression de cet employÃ©.")
            if st.button("Supprimer cet employÃ©"):
                if confirm_delete_employe:
                    supprimer_employe(employe_id)
                    st.success("EmployÃ© supprimÃ© avec succÃ¨s.")
                    st.rerun()
                else:
                    st.warning("Tu dois confirmer la suppression.")

elif menu == "Fiche organisme":
    orgs = get_organisations()

    if orgs.empty:
        st.info("Aucun organisme disponible.")
    else:
        options = {f"{row['nom']} (ID {row['id']})": row["id"] for _, row in orgs.iterrows()}
        labels = list(options.keys())
        default_index = 0

        if st.session_state.org_selectionnee in options.values():
            current_label = [k for k, v in options.items() if v == st.session_state.org_selectionnee][0]
            default_index = labels.index(current_label)

        selection = st.selectbox("SÃ©lectionner un organisme", labels, index=default_index, key="fiche_org_selectbox")
        st.session_state.org_selectionnee = options[selection]
        org_id = st.session_state.org_selectionnee
        org = get_organisation_by_id(org_id)

        if org is None:
            st.error("Organisme introuvable.")
        else:
            employe_attitre_nom = "-"
            if org["employe_id_attitre"]:
                emp_attitre = get_employe_by_id(org["employe_id_attitre"])
                if emp_attitre is not None:
                    employe_attitre_nom = emp_attitre["nom"]

            st.subheader(f"Fiche de : {org['nom']}")
            st.write(f"**Ville** : {org['ville'] if org['ville'] else '-'}")
            st.write(f"**Statut** : {org['statut'] if org['statut'] else '-'}")
            st.write(f"**EmployÃ© attitrÃ©** : {employe_attitre_nom}")
            st.write(f"**Notes** : {org['notes'] if org['notes'] else '-'}")

            st.markdown("### Modifier l'organisme")

            types_disponibles = ["", "OBNL", "CoopÃ©rative", "Entreprise d'Ã©conomie sociale", "Institution", "Autre"]
            statuts_disponibles = ["Actif", "En dÃ©marrage", "Ã€ relancer", "Inactif"]

            employes = get_employes()
            options_employes = {"Aucun employÃ© attitrÃ©": None}
            for _, row in employes.iterrows():
                options_employes[f"{row['nom']} (ID {row['id']})"] = row["id"]

            labels_employes = list(options_employes.keys())
            label_attitre_actuel = "Aucun employÃ© attitrÃ©"
            for label, value in options_employes.items():
                if value == org["employe_id_attitre"]:
                    label_attitre_actuel = label
                    break

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
                    telephone_mod = st.text_input("TÃ©lÃ©phone", value=org["telephone"] if org["telephone"] else "")

                with col2:
                    courriel_mod = st.text_input("Courriel", value=org["courriel"] if org["courriel"] else "")
                    statut_mod = st.selectbox(
                        "Statut",
                        statuts_disponibles,
                        index=statuts_disponibles.index(org["statut"]) if org["statut"] in statuts_disponibles else 0
                    )
                    employe_attitre_mod = st.selectbox(
                        "EmployÃ© attitrÃ© Ã  l'organisme",
                        labels_employes,
                        index=labels_employes.index(label_attitre_actuel)
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
                            notes_mod.strip(),
                            options_employes[employe_attitre_mod]
                        )
                        st.success("Organisme modifiÃ© avec succÃ¨s.")
                        st.rerun()

            st.markdown("### Contacts liÃ©s")
            contacts_org = get_contacts_by_organisation(org_id)

            with st.form("form_contact", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    contact_nom = st.text_input("Nom du contact *")
                    contact_role = st.text_input("RÃ´le / fonction")
                    contact_telephone = st.text_input("TÃ©lÃ©phone")
                with c2:
                    contact_courriel = st.text_input("Courriel")
                    contact_notes = st.text_area("Notes contact")

                submit_contact = st.form_submit_button("Ajouter le contact")

                if submit_contact:
                    if not contact_nom.strip():
                        st.error("Le nom du contact est obligatoire.")
                    else:
                        ajouter_contact(org_id, contact_nom.strip(), contact_role.strip(), contact_telephone.strip(), contact_courriel.strip(), contact_notes.strip())
                        st.success("Contact ajoutÃ© avec succÃ¨s.")
                        st.rerun()

            if contacts_org.empty:
                st.info("Aucun contact pour cet organisme.")
            else:
                st.dataframe(contacts_org, use_container_width=True)

            st.markdown("### Suivis liÃ©s")
            suivis_org = get_suivis_by_organisation(org_id)
            if suivis_org.empty:
                st.info("Aucun suivi pour cet organisme.")
            else:
                st.dataframe(suivis_org, use_container_width=True)

            st.markdown("### TÃ¢ches liÃ©es")
            taches_org = get_taches_by_organisation(org_id)
            employes = get_employes()
            employe_options = {"Non assignÃ©": None}
            for _, row in employes.iterrows():
                employe_options[f"{row['nom']} (ID {row['id']})"] = row["id"]

            with st.form("form_tache_fiche", clear_on_submit=True):
                t1, t2 = st.columns(2)
                with t1:
                    tache_titre = st.text_input("Titre de la tÃ¢che *")
                    employe_label = st.selectbox("EmployÃ© assignÃ©", list(employe_options.keys()), key="employe_tache_fiche")
                    tache_echeance = st.date_input("Ã‰chÃ©ance", value=date.today(), key="echeance_fiche")
                with t2:
                    tache_statut = st.selectbox("Statut", ["Ã€ faire", "En cours", "TerminÃ©e"], key="statut_fiche")
                    tache_priorite = st.selectbox("PrioritÃ©", ["Basse", "Moyenne", "Haute"], key="priorite_fiche")
                    tache_notes = st.text_area("Notes de la tÃ¢che", key="notes_fiche")

                submit_tache = st.form_submit_button("Ajouter la tÃ¢che")

                if submit_tache:
                    if not tache_titre.strip():
                        st.error("Le titre de la tÃ¢che est obligatoire.")
                    else:
                        employe_id = employe_options[employe_label]
                        responsable_nom = ""
                        if employe_id is not None:
                            employe_obj = get_employe_by_id(employe_id)
                            responsable_nom = employe_obj["nom"] if employe_obj is not None else ""

                        ajouter_tache(
                            org_id,
                            employe_id,
                            tache_titre.strip(),
                            responsable_nom,
                            str(tache_echeance),
                            tache_statut,
                            tache_priorite,
                            tache_notes.strip()
                        )
                        st.success("TÃ¢che ajoutÃ©e avec succÃ¨s.")
                        st.rerun()

            if taches_org.empty:
                st.info("Aucune tÃ¢che liÃ©e Ã  cet organisme.")
            else:
                st.dataframe(taches_org, use_container_width=True)

elif menu == "Suivis":
    st.subheader("Ajouter un suivi")
    orgs = get_organisations()

    if orgs.empty:
        st.warning("Ajoute d'abord un organisme avant de crÃ©er un suivi.")
    else:
        options_orgs = {
            f"{row['nom']} ({row['ville']})" if row['ville'] else row['nom']: row["id"]
            for _, row in orgs.iterrows()
        }

        with st.form("form_suivi", clear_on_submit=True):
            organisation_label = st.selectbox("Organisme", list(options_orgs.keys()))
            date_suivi = st.date_input("Date du suivi", value=date.today())
            type_suivi = st.selectbox("Type de suivi", ["TÃ©lÃ©phone", "Courriel", "Rencontre", "Visite", "Autre"])
            resume = st.text_area("RÃ©sumÃ© du suivi *")
            prochaine_action = st.text_area("Prochaine action")

            submit_suivi = st.form_submit_button("Enregistrer le suivi")

            if submit_suivi:
                if not resume.strip():
                    st.error("Le rÃ©sumÃ© du suivi est obligatoire.")
                else:
                    ajouter_suivi(options_orgs[organisation_label], str(date_suivi), type_suivi, resume.strip(), prochaine_action.strip())
                    st.success("Suivi ajoutÃ© avec succÃ¨s.")
                    st.rerun()

    st.subheader("Historique des suivis")
    suivis = get_suivis()
    if suivis.empty:
        st.info("Aucun suivi enregistrÃ©.")
    else:
        st.dataframe(suivis, use_container_width=True)

elif menu == "TÃ¢ches":
    st.subheader("Planification des tÃ¢ches")

    orgs = get_organisations()
    employes = get_employes()

    options_orgs = {"Aucun organisme liÃ©": None}
    for _, row in orgs.iterrows():
        label = f"{row['nom']} ({row['ville']})" if row['ville'] else row['nom']
        options_orgs[label] = row["id"]

    options_employes = {"Non assignÃ©": None}
    for _, row in employes.iterrows():
        options_employes[f"{row['nom']} (ID {row['id']})"] = row["id"]

    with st.form("form_tache_generale", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            titre = st.text_input("Titre de la tÃ¢che *")
            org_label = st.selectbox("Organisme liÃ©", list(options_orgs.keys()))
            employe_label = st.selectbox("EmployÃ© assignÃ©", list(options_employes.keys()))
            echeance = st.date_input("Ã‰chÃ©ance", value=date.today(), key="echeance_generale")

        with col2:
            statut = st.selectbox("Statut", ["Ã€ faire", "En cours", "TerminÃ©e"], key="statut_general")
            priorite = st.selectbox("PrioritÃ©", ["Basse", "Moyenne", "Haute"], key="priorite_generale")
            notes = st.text_area("Notes")

        submit_tache_generale = st.form_submit_button("Enregistrer la tÃ¢che")

        if submit_tache_generale:
            if not titre.strip():
                st.error("Le titre de la tÃ¢che est obligatoire.")
            else:
                employe_id = options_employes[employe_label]
                responsable_nom = ""
                if employe_id is not None:
                    employe_obj = get_employe_by_id(employe_id)
                    responsable_nom = employe_obj["nom"] if employe_obj is not None else ""

                ajouter_tache(
                    options_orgs[org_label],
                    employe_id,
                    titre.strip(),
                    responsable_nom,
                    str(echeance),
                    statut,
                    priorite,
                    notes.strip()
                )
                st.success("TÃ¢che ajoutÃ©e avec succÃ¨s.")
                st.rerun()

    taches = get_taches()

    if taches.empty:
        st.info("Aucune tÃ¢che enregistrÃ©e.")
    else:
        f1, f2, f3 = st.columns(3)

        with f1:
            filtre_statut = st.selectbox("Filtrer par statut", ["Toutes", "Ã€ faire", "En cours", "TerminÃ©e"])

        with f2:
            filtre_employe = st.selectbox(
                "Filtrer par employÃ©",
                ["Tous"] + sorted([e for e in taches["employe_assigne"].dropna().unique() if str(e).strip() != "-"])
            )

        with f3:
            filtre_priorite = st.selectbox("Filtrer par prioritÃ©", ["Toutes", "Basse", "Moyenne", "Haute"])

        taches_filtrees = taches.copy()

        if filtre_statut != "Toutes":
            taches_filtrees = taches_filtrees[taches_filtrees["statut"] == filtre_statut]

        if filtre_employe != "Tous":
            taches_filtrees = taches_filtrees[taches_filtrees["employe_assigne"] == filtre_employe]

        if filtre_priorite != "Toutes":
            taches_filtrees = taches_filtrees[taches_filtrees["priorite"] == filtre_priorite]

        tab1, tab2 = st.tabs(["Vue tableau", "Vue par employÃ©"])

        with tab1:
            st.dataframe(taches_filtrees, use_container_width=True)

        with tab2:
            employes_liste = get_employes()
            if employes_liste.empty:
                st.info("Aucun employÃ© enregistrÃ©.")
            else:
                for _, emp in employes_liste.iterrows():
                    st.markdown(f"### {emp['nom']} â€” {emp['poste'] if emp['poste'] else 'Sans poste'}")
                    emp_tasks = get_taches_by_employe(emp["id"])
                    if emp_tasks.empty:
                        st.info("Aucune tÃ¢che assignÃ©e.")
                    else:
                        st.dataframe(emp_tasks, use_container_width=True)