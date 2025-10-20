"""
Application Locator - Gestion de Location Immobilière
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from src import database as db
from src import file_manager as fm
from src import quittance as qt
from src import email_alerts as ea
import os

# Configuration de la page
st.set_page_config(
    page_title="Locator - Gestion Locative",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation
if 'initialized' not in st.session_state:
    db.init_db()
    db.migrate_db()  # Ajoute les nouvelles tables si nécessaire
    fm.init_directories()
    st.session_state.initialized = True

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-danger {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .alert-success {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


# ==================== SIDEBAR - NAVIGATION ====================

st.sidebar.title("🏠 Locator")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🏢 Appartements", "👥 Locataires", "💰 Paiements", "📄 Factures", "📝 Quittances", "⚙️ Paramètres"]
)

st.sidebar.markdown("---")
st.sidebar.info("Application de gestion locative locale")


# ==================== DASHBOARD ====================

if menu == "📊 Dashboard":
    st.markdown("<h1 class='main-header'>📊 Tableau de Bord</h1>", unsafe_allow_html=True)
    
    # Récupérer les statistiques
    stats = db.get_statistiques()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏢 Appartements", stats['nb_appartements'])
        st.metric("🚪 Chambres totales", stats['nb_chambres'])
    
    with col2:
        st.metric("👥 Locataires actifs", stats['nb_locataires_actifs'])
        st.metric("📦 Chambres disponibles", stats['nb_chambres_disponibles'])
    
    with col3:
        st.metric("💰 Revenus mois actuel", f"{stats['revenus_mois_actuel']:.2f} €")
        st.metric("📈 Loyers attendus", f"{stats['loyers_attendus']:.2f} €")
    
    with col4:
        st.metric("📊 Taux d'occupation", f"{stats['taux_occupation']:.1f}%")
        st.metric("⚠️ Paiements impayés", stats['nb_paiements_impayés'])
    
    st.markdown("---")
    
    # Alertes
    if stats['nb_paiements_impayés'] > 0:
        st.markdown("<div class='alert-danger'>", unsafe_allow_html=True)
        st.warning(f"⚠️ {stats['nb_paiements_impayés']} paiement(s) en retard - Action requise")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Afficher les détails des impayés
        paiements_impayés = db.get_paiements_impayés()
        if paiements_impayés:
            st.subheader("Détails des impayés")
            
            impayés_data = []
            for p in paiements_impayés:
                locataire = db.get_locataire_by_id(p.locataire_id)
                chambre = db.get_chambre_by_id(p.chambre_id)
                
                impayés_data.append({
                    'Locataire': locataire.nom,
                    'Chambre': chambre.numero,
                    'Mois': f"{p.mois}/{p.annee}",
                    'Montant': f"{p.montant:.2f} €",
                    'Statut': p.statut
                })
            
            df_impayés = pd.DataFrame(impayés_data)
            st.dataframe(df_impayés, use_container_width=True)
    
    # Graphiques
    st.markdown("---")
    st.subheader("📈 Analyses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique d'occupation
        labels = ['Occupées', 'Disponibles']
        values = [stats['nb_chambres'] - stats['nb_chambres_disponibles'], stats['nb_chambres_disponibles']]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        fig.update_layout(title_text="Taux d'occupation des chambres")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Graphique des revenus (exemple simplifié)
        # TODO: Ajouter un graphique d'évolution des revenus mensuels
        st.info("📊 Graphique d'évolution des revenus - À venir")


# ==================== APPARTEMENTS ====================

elif menu == "🏢 Appartements":
    st.markdown("<h1 class='main-header'>🏢 Gestion des Appartements</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Liste des appartements", "➕ Ajouter un appartement"])
    
    with tab1:
        appartements = db.get_all_appartements()
        
        if not appartements:
            st.info("Aucun appartement enregistré. Ajoutez-en un dans l'onglet 'Ajouter'.")
        else:
            for appt in appartements:
                with st.expander(f"📍 {appt.adresse} - {appt.ville}"):
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write(f"**Surface:** {appt.surface} m²")
                            st.write(f"**Code postal:** {appt.code_postal}")
                        
                        with col_b:
                            if appt.date_acquisition:
                                st.write(f"**Date d'acquisition:** {appt.date_acquisition.strftime('%d/%m/%Y')}")
                            if appt.notes:
                                st.write(f"**Notes:** {appt.notes}")
                    
                    with col2:
                        # Initialiser l'état d'édition avant le bouton
                        edit_key = f'edit_appt_{appt.id}'
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                        
                        if st.button("✏️ Modifier", key=f"btn_edit_appt_{appt.id}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                        if st.button("🗑️ Supprimer", key=f"del_appt_{appt.id}"):
                            if db.delete_appartement(appt.id):
                                st.success("Appartement supprimé")
                                st.rerun()
                    
                    # Formulaire de modification
                    if st.session_state.get(f'edit_appt_{appt.id}', False):
                        st.markdown("---")
                        st.subheader("✏️ Modifier l'appartement")
                        with st.form(key=f"form_edit_appt_{appt.id}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_adresse = st.text_input("Adresse", value=appt.adresse)
                                new_ville = st.text_input("Ville", value=appt.ville)
                                new_surface = st.number_input("Surface (m²)", min_value=0.0, value=float(appt.surface))
                            
                            with col2:
                                new_code_postal = st.text_input("Code postal", value=appt.code_postal)
                                new_date_acquisition = st.date_input("Date d'acquisition", value=appt.date_acquisition)
                            
                            new_notes = st.text_area("Notes", value=appt.notes or "")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                if st.form_submit_button("💾 Enregistrer les modifications"):
                                    db.update_appartement(
                                        appt.id,
                                        adresse=new_adresse,
                                        ville=new_ville,
                                        code_postal=new_code_postal,
                                        surface=new_surface,
                                        date_acquisition=new_date_acquisition,
                                        notes=new_notes
                                    )
                                    st.session_state[f'edit_appt_{appt.id}'] = False
                                    st.success("Appartement modifié avec succès!")
                                    st.rerun()
                            with col_b:
                                if st.form_submit_button("❌ Annuler"):
                                    st.session_state[f'edit_appt_{appt.id}'] = False
                                    st.rerun()
                    
                    st.markdown("---")
                    st.subheader("🚪 Chambres")
                    
                    # Afficher les chambres
                    chambres = db.get_chambres_by_appartement(appt.id)
                    if chambres:
                        for ch in chambres:
                            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
                            with col_a:
                                type_log = "🏢 Appt. complet" if ch.est_appartement_complet else "🚪 Chambre"
                                st.write(f"**{type_log}: {ch.numero}**")
                            with col_b:
                                st.write(f"Loyer: {ch.loyer:.2f} € | Charges: {ch.charges:.2f} €")
                            with col_c:
                                status = "✅ Disponible" if ch.disponible else "🔒 Occupée"
                                st.write(status)
                            with col_d:
                                if st.button("🗑️", key=f"del_ch_{ch.id}"):
                                    if db.delete_chambre(ch.id):
                                        st.success("Chambre supprimée")
                                        st.rerun()
                    else:
                        st.info("Aucune chambre définie")
                    
                    # Ajouter une chambre
                    st.markdown("**➕ Ajouter une chambre/logement**")
                    with st.form(key=f"form_add_ch_{appt.id}"):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            ch_numero = st.text_input("Numéro/Nom", key=f"ch_num_{appt.id}")
                        with col2:
                            ch_loyer = st.number_input("Loyer (€)", min_value=0.0, key=f"ch_loyer_{appt.id}")
                        with col3:
                            ch_charges = st.number_input("Charges (€)", min_value=0.0, key=f"ch_charges_{appt.id}")
                        with col4:
                            ch_complet = st.checkbox("Appt. complet", key=f"ch_complet_{appt.id}")
                        
                        if st.form_submit_button("Ajouter"):
                            if ch_numero and ch_loyer > 0:
                                db.create_chambre(appt.id, ch_numero, ch_loyer, ch_charges, est_appartement_complet=ch_complet)
                                st.success("Chambre/Logement ajouté avec succès!")
                                st.rerun()
                            else:
                                st.error("Veuillez remplir tous les champs requis")
    
    with tab2:
        st.subheader("➕ Nouvel Appartement")
        
        with st.form("form_appartement"):
            col1, col2 = st.columns(2)
            
            with col1:
                adresse = st.text_input("Adresse *")
                ville = st.text_input("Ville *")
                surface = st.number_input("Surface (m²) *", min_value=0.0)
            
            with col2:
                code_postal = st.text_input("Code postal *")
                date_acquisition = st.date_input("Date d'acquisition", value=None)
            
            notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("💾 Enregistrer l'appartement")
            
            if submitted:
                if adresse and ville and code_postal and surface > 0:
                    db.create_appartement(
                        adresse=adresse,
                        ville=ville,
                        code_postal=code_postal,
                        surface=surface,
                        date_acquisition=date_acquisition,
                        notes=notes
                    )
                    st.success("✅ Appartement enregistré avec succès!")
                    st.rerun()
                else:
                    st.error("⚠️ Veuillez remplir tous les champs obligatoires (*)")


# ==================== LOCATAIRES ====================

elif menu == "👥 Locataires":
    st.markdown("<h1 class='main-header'>👥 Gestion des Locataires & Baux</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Liste des baux", "➕ Créer un bail", "👤 Locataires sans bail"])
    
    with tab1:
        bails = db.get_all_bails()
        
        if not bails:
            st.info("Aucun bail enregistré. Créez-en un dans l'onglet 'Créer un bail'.")
        else:
            # Filtres
            col1, col2 = st.columns([3, 1])
            with col2:
                filtre_actif = st.checkbox("Actifs seulement", value=True, key="filtre_bails")
            
            bails_filtres = [b for b in bails if not filtre_actif or b.actif]
            
            for bail in bails_filtres:
                statut_emoji = "✅" if bail.actif else "❌"
                chambre = db.get_chambre_by_id(bail.chambre_id)
                appt = db.get_appartement_by_id(chambre.appartement_id)
                locataires = [l for l in db.get_all_locataires() if l.bail_id == bail.id]
                
                type_log = "Appartement complet" if chambre.est_appartement_complet else f"Chambre {chambre.numero}"
                titre = f"{statut_emoji} {appt.adresse} - {type_log}"
                if locataires:
                    noms = ", ".join([l.nom for l in locataires])
                    titre += f" | {noms}"
                
                with st.expander(titre):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📍 Adresse:** {appt.adresse}, {appt.code_postal} {appt.ville}")
                        st.write(f"**🚪 Logement:** {type_log}")
                        st.write(f"**💰 Loyer:** {bail.loyer_total:.2f} € + {bail.charges_total:.2f} € de charges")
                    
                    with col2:
                        st.write(f"**📅 Début du bail:** {bail.date_debut.strftime('%d/%m/%Y')}")
                        if bail.date_fin:
                            st.write(f"**📅 Fin du bail:** {bail.date_fin.strftime('%d/%m/%Y')}")
                        if bail.notes:
                            st.write(f"**📝 Notes:** {bail.notes}")
                    
                    # Bouton pour modifier le loyer
                    if st.button("✏️ Modifier le loyer", key=f"edit_loyer_{bail.id}"):
                        st.session_state[f'editing_loyer_{bail.id}'] = True
                    
                    # Formulaire de modification du loyer
                    if st.session_state.get(f'editing_loyer_{bail.id}', False):
                        st.markdown("---")
                        st.subheader("💰 Modification du loyer")
                        
                        # Afficher l'historique s'il existe
                        historiques = db.get_historique_by_bail(bail.id)
                        if historiques:
                            st.markdown("**📜 Historique des loyers:**")
                            for hist in historiques:
                                st.info(f"**{hist.date_application.strftime('%d/%m/%Y')}**: {hist.ancien_loyer:.2f} € → {hist.nouveau_loyer:.2f} € (Charges: {hist.anciennes_charges:.2f} € → {hist.nouvelles_charges:.2f} €) - {hist.notes}")
                        
                        with st.form(key=f"form_edit_loyer_{bail.id}"):
                            st.write(f"**Loyer actuel:** {bail.loyer_total:.2f} €")
                            st.write(f"**Charges actuelles:** {bail.charges_total:.2f} €")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                nouveau_loyer = st.number_input("Nouveau loyer *", min_value=0.0, value=float(bail.loyer_total), step=10.0, key=f"new_loyer_{bail.id}")
                            with col2:
                                nouvelles_charges = st.number_input("Nouvelles charges *", min_value=0.0, value=float(bail.charges_total), step=5.0, key=f"new_charges_{bail.id}")
                            with col3:
                                date_application = st.date_input("Date d'application *", value=datetime.now().date(), key=f"date_app_{bail.id}")
                            
                            notes_modif = st.text_area("Notes sur cette modification", key=f"notes_modif_{bail.id}")
                            
                            st.warning("⚠️ Cette modification mettra à jour tous les paiements futurs à partir de la date d'application.")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("💾 Enregistrer la modification"):
                                    try:
                                        bail_updated, nb_paiements = db.update_bail_loyer(
                                            bail.id,
                                            nouveau_loyer,
                                            nouvelles_charges,
                                            date_application,
                                            notes_modif
                                        )
                                        st.success(f"✅ Loyer modifié avec succès! {nb_paiements} paiements ont été mis à jour.")
                                        del st.session_state[f'editing_loyer_{bail.id}']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Erreur: {str(e)}")
                            with col_btn2:
                                if st.form_submit_button("❌ Annuler"):
                                    del st.session_state[f'editing_loyer_{bail.id}']
                                    st.rerun()
                    
                    st.markdown("---")
                    st.subheader("👥 Locataires sur ce bail")
                    
                    if not locataires:
                        st.warning("Aucun locataire assigné à ce bail")
                    else:
                        for loc in locataires:
                            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
                            with col_a:
                                st.write(f"**{loc.nom}**")
                            with col_b:
                                st.write(f"📧 {loc.email or 'N/A'}")
                                st.write(f"📞 {loc.telephone or 'N/A'}")
                            with col_c:
                                if loc.part_loyer:
                                    st.write(f"💰 Part: {loc.part_loyer:.2f} €")
                                st.write(f"🔒 Caution: {loc.depot_garantie:.2f} €")
                            with col_d:
                                if st.button("🗑️", key=f"del_loc_{loc.id}"):
                                    if db.delete_locataire(loc.id):
                                        st.success("Locataire retiré")
                                        st.rerun()
                    
                    # Ajouter un locataire au bail
                    st.markdown("**➕ Ajouter un locataire à ce bail**")
                    with st.form(key=f"form_add_loc_{bail.id}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            loc_nom = st.text_input("Nom complet *", key=f"loc_nom_{bail.id}")
                            loc_email = st.text_input("Email", key=f"loc_email_{bail.id}")
                        with col2:
                            loc_telephone = st.text_input("Téléphone", key=f"loc_tel_{bail.id}")
                            loc_part_loyer = st.number_input("Part du loyer (€)", min_value=0.0, key=f"loc_part_{bail.id}", 
                                                            help="Laisser à 0 si loyer partagé équitablement")
                        with col3:
                            loc_caution = st.number_input("Caution (€)", min_value=0.0, key=f"loc_caution_{bail.id}")
                            loc_date_entree = st.date_input("Date d'entrée", value=bail.date_debut, key=f"loc_date_{bail.id}")
                        
                        loc_notes = st.text_area("Notes", key=f"loc_notes_{bail.id}")
                        
                        if st.form_submit_button("Ajouter le locataire"):
                            if loc_nom:
                                db.create_locataire(
                                    nom=loc_nom,
                                    email=loc_email,
                                    telephone=loc_telephone,
                                    date_entree=loc_date_entree,
                                    bail_id=bail.id,
                                    depot_garantie=loc_caution,
                                    part_loyer=loc_part_loyer if loc_part_loyer > 0 else None,
                                    notes=loc_notes
                                )
                                st.success("Locataire ajouté au bail!")
                                st.rerun()
                            else:
                                st.error("Nom requis")
                    
                    # Actions sur le bail
                    st.markdown("---")
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        if bail.actif:
                            if st.button("🔒 Clôturer le bail", key=f"close_bail_{bail.id}"):
                                db.update_bail(bail.id, actif=False, date_fin=date.today())
                                # Libérer la chambre
                                db.update_chambre(bail.chambre_id, disponible=True)
                                # Désactiver les locataires
                                for loc in locataires:
                                    db.update_locataire(loc.id, actif=False, date_sortie=date.today())
                                st.success("Bail clôturé")
                                st.rerun()
                    with col_b:
                        if st.button("🗑️ Supprimer le bail", key=f"del_bail_{bail.id}"):
                            if db.delete_bail(bail.id):
                                st.success("Bail supprimé")
                                st.rerun()
    
    with tab2:
        st.subheader("➕ Créer un nouveau bail")
        
        # Sélectionner une chambre disponible
        chambres_dispo = [c for c in db.get_all_chambres() if c.disponible]
        
        if not chambres_dispo:
            st.warning("⚠️ Aucune chambre/logement disponible. Ajoutez d'abord un appartement et des chambres.")
        else:
            with st.form("form_nouveau_bail"):
                st.markdown("### 📋 Informations du bail")
                
                # Sélection du logement
                chambre_options = {}
                for ch in chambres_dispo:
                    appt = db.get_appartement_by_id(ch.appartement_id)
                    type_log = "Appt. complet" if ch.est_appartement_complet else f"Chambre {ch.numero}"
                    label = f"{appt.adresse} - {type_log} ({ch.loyer + ch.charges:.2f} €)"
                    chambre_options[label] = ch
                
                chambre_selectionnee = st.selectbox("Logement", list(chambre_options.keys()))
                chambre = chambre_options[chambre_selectionnee]
                
                col1, col2 = st.columns(2)
                with col1:
                    bail_loyer = st.number_input("Loyer total (€)", min_value=0.0, value=float(chambre.loyer))
                    bail_charges = st.number_input("Charges totales (€)", min_value=0.0, value=float(chambre.charges))
                with col2:
                    bail_debut = st.date_input("Date de début", value=date.today())
                    bail_fin = st.date_input("Date de fin (optionnelle)", value=None)
                
                bail_notes = st.text_area("Notes sur le bail")
                
                st.markdown("---")
                st.markdown("### 👥 Premier locataire (vous pourrez en ajouter d'autres après)")
                
                col1, col2 = st.columns(2)
                with col1:
                    loc_nom = st.text_input("Nom complet *")
                    loc_email = st.text_input("Email")
                    loc_telephone = st.text_input("Téléphone")
                with col2:
                    loc_caution = st.number_input("Dépôt de garantie (€)", min_value=0.0)
                    loc_part = st.number_input("Part du loyer (€)", min_value=0.0, 
                                              help="Laisser à 0 si locataire unique ou loyer partagé équitablement")
                
                loc_notes = st.text_area("Notes sur le locataire")
                
                submitted = st.form_submit_button("💾 Créer le bail et ajouter le locataire")
                
                if submitted:
                    if loc_nom:
                        # Créer le bail (retourne maintenant l'ID)
                        nouveau_bail_id = db.create_bail(
                            chambre_id=chambre.id,
                            date_debut=bail_debut,
                            date_fin=bail_fin,
                            loyer_total=bail_loyer,
                            charges_total=bail_charges,
                            notes=bail_notes
                        )
                        
                        # Créer le locataire
                        db.create_locataire(
                            nom=loc_nom,
                            email=loc_email,
                            telephone=loc_telephone,
                            date_entree=bail_debut,
                            bail_id=nouveau_bail_id,
                            depot_garantie=loc_caution,
                            part_loyer=loc_part if loc_part > 0 else None,
                            notes=loc_notes
                        )
                        
                        # Créer les paiements pour l'année
                        mois_debut = bail_debut.month
                        annee_debut = bail_debut.year
                        
                        for mois in range(mois_debut, 13):
                            # Pour l'instant, on crée un paiement global (à adapter si plusieurs locataires)
                            locataire_cree = [l for l in db.get_all_locataires() if l.bail_id == nouveau_bail_id][0]
                            db.create_paiement(
                                locataire_id=locataire_cree.id,
                                chambre_id=chambre.id,
                                mois=mois,
                                annee=annee_debut,
                                montant=bail_loyer + bail_charges,
                                statut='impaye'
                            )
                        
                        st.success("✅ Bail créé et locataire ajouté avec succès!")
                        st.rerun()
                    else:
                        st.error("⚠️ Nom du locataire requis")
    
    with tab3:
        st.subheader("👤 Locataires sans bail actif")
        
        tous_locataires = db.get_all_locataires()
        locataires_sans_bail = [l for l in tous_locataires if l.bail_id is None or not l.actif]
        
        if not locataires_sans_bail:
            st.info("Tous les locataires sont assignés à un bail")
        else:
            for loc in locataires_sans_bail:
                with st.expander(f"👤 {loc.nom}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email:** {loc.email or 'N/A'}")
                        st.write(f"**Téléphone:** {loc.telephone or 'N/A'}")
                    with col2:
                        st.write(f"**Date d'entrée:** {loc.date_entree.strftime('%d/%m/%Y')}")
                        if loc.date_sortie:
                            st.write(f"**Date de sortie:** {loc.date_sortie.strftime('%d/%m/%Y')}")
                    
                    if st.button(f"🗑️ Supprimer {loc.nom}", key=f"del_orphan_{loc.id}"):
                        if db.delete_locataire(loc.id):
                            st.success("Locataire supprimé")
                            st.rerun()


# ==================== PAIEMENTS ====================

elif menu == "💰 Paiements":
    st.markdown("<h1 class='main-header'>💰 Suivi des Paiements</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Tous les paiements", "➕ Enregistrer un paiement", "🧾 Quittances"])
    
    with tab1:
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            annee_filtre = st.selectbox("Année", [datetime.now().year - 1, datetime.now().year, datetime.now().year + 1])
        with col2:
            mois_filtre = st.selectbox("Mois", ["Tous"] + list(range(1, 13)), format_func=lambda x: "Tous" if x == "Tous" else f"{x}")
        with col3:
            statut_filtre = st.selectbox("Statut", ["Tous", "paye", "impaye", "partiel"])
        
        # Récupérer les paiements
        if mois_filtre == "Tous":
            paiements = [p for p in db.get_all_paiements() if p.annee == annee_filtre]
        else:
            paiements = db.get_paiements_by_mois_annee(mois_filtre, annee_filtre)
        
        if statut_filtre != "Tous":
            paiements = [p for p in paiements if p.statut == statut_filtre]
        
        if not paiements:
            st.info("Aucun paiement trouvé avec ces critères")
        else:
            # Créer le DataFrame
            paiements_data = []
            for p in paiements:
                locataire = db.get_locataire_by_id(p.locataire_id)
                chambre = db.get_chambre_by_id(p.chambre_id)
                
                paiements_data.append({
                    'ID': p.id,
                    'Locataire': locataire.nom,
                    'Chambre': chambre.numero,
                    'Période': f"{p.mois:02d}/{p.annee}",
                    'Montant': f"{p.montant:.2f} €",
                    'Statut': p.statut,
                    'Date paiement': p.date_paiement.strftime('%d/%m/%Y') if p.date_paiement else 'N/A',
                    'Mode': p.mode_paiement or 'N/A'
                })
            
            df = pd.DataFrame(paiements_data)
            
            # Colorier par statut
            def highlight_statut(row):
                if row['Statut'] == 'paye':
                    return ['background-color: #e8f5e9'] * len(row)
                elif row['Statut'] == 'impaye':
                    return ['background-color: #ffebee'] * len(row)
                else:
                    return ['background-color: #fff3e0'] * len(row)
            
            st.dataframe(df.style.apply(highlight_statut, axis=1), use_container_width=True, hide_index=True)
            
            # Statistiques rapides
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_attendu = sum([p.montant for p in paiements])
                st.metric("💵 Total attendu", f"{total_attendu:.2f} €")
            with col2:
                total_recu = sum([p.montant for p in paiements if p.statut == 'paye'])
                st.metric("✅ Total reçu", f"{total_recu:.2f} €")
            with col3:
                total_impaye = sum([p.montant for p in paiements if p.statut == 'impaye'])
                st.metric("⚠️ Total impayé", f"{total_impaye:.2f} €")
    
    with tab2:
        st.subheader("➕ Enregistrer un paiement")
        
        # Sélectionner un locataire actif
        locataires_actifs = db.get_all_locataires(actifs_seulement=True)
        
        if not locataires_actifs:
            st.warning("Aucun locataire actif")
        else:
            locataire_options = {l.nom: l.id for l in locataires_actifs}
            locataire_selectionne = st.selectbox("Locataire", list(locataire_options.keys()))
            locataire_id = locataire_options[locataire_selectionne]
            
            # Récupérer les paiements de ce locataire
            paiements_locataire = db.get_paiements_by_locataire(locataire_id)
            paiements_impayés = [p for p in paiements_locataire if p.statut == 'impaye']
            
            if not paiements_impayés:
                st.info("Aucun paiement en attente pour ce locataire")
            else:
                paiement_options = {f"{p.mois:02d}/{p.annee} - {p.montant:.2f} €": p.id for p in paiements_impayés}
                paiement_selectionne = st.selectbox("Paiement à enregistrer", list(paiement_options.keys()))
                paiement_id = paiement_options[paiement_selectionne]
                
                with st.form("form_paiement"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        date_paiement = st.date_input("Date du paiement", value=date.today())
                        mode_paiement = st.selectbox("Mode de paiement", ["virement", "cheque", "especes", "autre"])
                    
                    with col2:
                        statut_paiement = st.selectbox("Statut", ["paye", "partiel"])
                        montant_recu = st.number_input("Montant reçu (€)", min_value=0.0)
                    
                    notes = st.text_area("Notes")
                    generer_quittance = st.checkbox("Générer une quittance", value=True)
                    
                    submitted = st.form_submit_button("💾 Enregistrer")
                    
                    if submitted:
                        # Mettre à jour le paiement
                        db.update_paiement(
                            paiement_id,
                            date_paiement=date_paiement,
                            mode_paiement=mode_paiement,
                            statut=statut_paiement,
                            notes=notes
                        )
                        
                        # Générer la quittance si demandé
                        if generer_quittance and statut_paiement == 'paye':
                            paiement = db.get_all_paiements()  # Recharger
                            paiement = [p for p in paiement if p.id == paiement_id][0]
                            
                            locataire = db.get_locataire_by_id(locataire_id)
                            chambre = db.get_chambre_by_id(paiement.chambre_id)
                            appt = db.get_appartement_by_id(chambre.appartement_id)
                            
                            # Générer la quittance
                            quittance_path = qt.generer_quittance_simple(
                                locataire, chambre, appt, paiement, paiement.mois, paiement.annee
                            )
                            
                            # Sauvegarder dans le répertoire du locataire
                            final_path = fm.save_quittance_file(
                                quittance_path, locataire.nom,
                                paiement.annee, paiement.mois
                            )
                            
                            # Marquer comme quittance générée
                            db.update_paiement(paiement_id, quittance_generee=True)
                            
                            st.success(f"✅ Paiement enregistré et quittance générée : {final_path}")
                        else:
                            st.success("✅ Paiement enregistré avec succès!")
                        
                        st.rerun()
    
    with tab3:
        st.subheader("🧾 Génération de quittances")
        
        locataires_actifs = db.get_all_locataires(actifs_seulement=True)
        
        if not locataires_actifs:
            st.warning("Aucun locataire actif")
        else:
            locataire_options = {l.nom: l for l in locataires_actifs}
            locataire_selectionne = st.selectbox("Sélectionner un locataire", list(locataire_options.keys()))
            locataire = locataire_options[locataire_selectionne]
            
            col1, col2 = st.columns(2)
            with col1:
                annee_quittance = st.number_input("Année", min_value=2020, max_value=2030, value=datetime.now().year)
            with col2:
                mois_quittance = st.number_input("Mois", min_value=1, max_value=12, value=datetime.now().month)
            
            if st.button("🧾 Générer la quittance"):
                # Chercher le paiement correspondant
                paiements = db.get_paiements_by_mois_annee(mois_quittance, annee_quittance)
                paiement = next((p for p in paiements if p.locataire_id == locataire.id), None)
                
                if not paiement:
                    st.error("Aucun paiement trouvé pour cette période")
                elif paiement.statut != 'paye':
                    st.warning("Le paiement n'est pas marqué comme payé")
                else:
                    chambre = db.get_chambre_by_id(paiement.chambre_id)
                    appt = db.get_appartement_by_id(chambre.appartement_id)
                    
                    quittance_path = qt.generer_quittance_simple(
                        locataire, chambre, appt, paiement, mois_quittance, annee_quittance
                    )
                    
                    final_path = fm.save_quittance_file(
                        quittance_path, locataire.nom,
                        annee_quittance, mois_quittance
                    )
                    
                    db.update_paiement(paiement.id, quittance_generee=True)
                    
                    st.success(f"✅ Quittance générée : {final_path}")
                    
                    # Proposer le téléchargement
                    with open(final_path, 'rb') as f:
                        st.download_button(
                            label="📥 Télécharger la quittance",
                            data=f,
                            file_name=os.path.basename(final_path),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )


# ==================== FACTURES ====================

elif menu == "📄 Factures":
    st.markdown("<h1 class='main-header'>📄 Gestion des Factures</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Liste des factures", "➕ Ajouter une facture"])
    
    with tab1:
        factures = db.get_all_factures()
        
        if not factures:
            st.info("Aucune facture enregistrée")
        else:
            # Filtres
            categories = list(set([f.categorie for f in factures]))
            categorie_filtre = st.selectbox("Catégorie", ["Toutes"] + categories)
            
            factures_filtrees = factures if categorie_filtre == "Toutes" else [f for f in factures if f.categorie == categorie_filtre]
            
            # Affichage
            factures_data = []
            for f in factures_filtrees:
                appt = db.get_appartement_by_id(f.appartement_id)
                factures_data.append({
                    'Date': f.date_facture.strftime('%d/%m/%Y'),
                    'Appartement': appt.adresse,
                    'Catégorie': f.categorie,
                    'Fournisseur': f.fournisseur or 'N/A',
                    'Montant': f"{f.montant:.2f} €",
                    'Statut': f.statut,
                    'Description': f.description or ''
                })
            
            df = pd.DataFrame(factures_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Stats
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                total = sum([f.montant for f in factures_filtrees])
                st.metric("💰 Total des factures", f"{total:.2f} €")
            with col2:
                impayees = sum([f.montant for f in factures_filtrees if f.statut == 'impaye'])
                st.metric("⚠️ Factures impayées", f"{impayees:.2f} €")
    
    with tab2:
        st.subheader("➕ Nouvelle Facture")
        
        appartements = db.get_all_appartements()
        
        if not appartements:
            st.warning("Aucun appartement enregistré")
        else:
            appt_options = {f"{a.adresse} - {a.ville}": a.id for a in appartements}
            
            with st.form("form_facture"):
                appt_selectionne = st.selectbox("Appartement", list(appt_options.keys()))
                appt_id = appt_options[appt_selectionne]
                
                col1, col2 = st.columns(2)
                with col1:
                    categorie = st.selectbox("Catégorie", ["travaux", "electricite", "eau", "gaz", "assurance", "entretien", "taxe fonciere", "autre"])
                    fournisseur = st.text_input("Fournisseur")
                    montant = st.number_input("Montant (€)", min_value=0.0)
                
                with col2:
                    date_facture = st.date_input("Date de la facture", value=date.today())
                    statut = st.selectbox("Statut", ["impaye", "paye"])
                    if statut == "paye":
                        date_paiement = st.date_input("Date de paiement", value=date.today())
                    else:
                        date_paiement = None
                
                description = st.text_area("Description")
                fichier = st.file_uploader("Joindre un fichier (PDF, image)", type=['pdf', 'jpg', 'jpeg', 'png'])
                
                submitted = st.form_submit_button("💾 Enregistrer la facture")
                
                if submitted:
                    if montant > 0:
                        # Sauvegarder le fichier si fourni
                        fichier_path = ""
                        if fichier:
                            appt = db.get_appartement_by_id(appt_id)
                            fichier_path = fm.save_facture_file(
                                fichier,
                                appt.adresse,
                                date_facture.year,
                                fichier.name
                            )
                        
                        # Créer la facture
                        db.create_facture(
                            appartement_id=appt_id,
                            categorie=categorie,
                            montant=montant,
                            date_facture=date_facture,
                            fournisseur=fournisseur,
                            description=description,
                            fichier_path=fichier_path,
                            statut=statut
                        )
                        
                        st.success("✅ Facture enregistrée avec succès!")
                        st.rerun()
                    else:
                        st.error("Le montant doit être supérieur à 0")


# ==================== QUITTANCES ====================

elif menu == "📝 Quittances":
    st.markdown("<h1 class='main-header'>📝 Gestion des Quittances</h1>", unsafe_allow_html=True)
    
    st.subheader("📋 Liste des quittances")
    
    # Sélection de l'appartement
    appartements = db.get_all_appartements()
    if not appartements:
        st.warning("Aucun appartement enregistré")
    else:
        appt_options = {f"{a.adresse} - {a.ville}": a for a in appartements}
        appt_selectionne_nom = st.selectbox("🏢 Sélectionner un appartement", list(appt_options.keys()))
        appt_selectionne = appt_options[appt_selectionne_nom]
        
        # Récupérer les chambres de l'appartement
        chambres = db.get_chambres_by_appartement(appt_selectionne.id)
        
        if not chambres:
            st.info("Aucune chambre/bail enregistré pour cet appartement")
        else:
            # Récupérer tous les locataires actifs de cet appartement
            tous_locataires = []
            for chambre in chambres:
                bails = db.get_bails_by_chambre(chambre.id)
                for bail in bails:
                    if bail.actif:
                        locataires = [l for l in db.get_all_locataires() if l.bail_id == bail.id and l.actif]
                        for loc in locataires:
                            tous_locataires.append({
                                'locataire': loc,
                                'bail': bail,
                                'chambre': chambre
                            })
            
            if not tous_locataires:
                st.info("Aucun locataire actif dans cet appartement")
            else:
                # Sélection du/des locataires
                loc_options = {f"{l['locataire'].nom} - {l['chambre'].numero if not l['chambre'].est_appartement_complet else 'Appartement complet'}": l for l in tous_locataires}
                loc_selectionne_nom = st.selectbox("👤 Sélectionner un locataire", list(loc_options.keys()))
                loc_data = loc_options[loc_selectionne_nom]
                
                locataire = loc_data['locataire']
                bail = loc_data['bail']
                chambre = loc_data['chambre']
                
                st.markdown("---")
                
                # Afficher les informations du bail
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Locataire :** {locataire.nom}")
                    st.write(f"**Logement :** {chambre.numero if not chambre.est_appartement_complet else 'Appartement complet'}")
                    st.write(f"**Loyer :** {bail.loyer_total:.2f} €")
                    st.write(f"**Charges :** {bail.charges_total:.2f} €")
                with col2:
                    st.write(f"**Total mensuel :** {bail.loyer_total + bail.charges_total:.2f} €")
                    if locataire.part_loyer:
                        st.write(f"**Part du locataire :** {locataire.part_loyer:.2f} €")
                
                st.markdown("---")
                
                # Récupérer les paiements du locataire
                paiements = db.get_paiements_by_locataire(locataire.id)
                
                if not paiements:
                    st.info("Aucun paiement enregistré pour ce locataire")
                else:
                    # Afficher les quittances disponibles
                    st.subheader("📄 Quittances disponibles")
                    
                    # Préparer les données
                    from datetime import datetime
                    date_aujourdhui = datetime.now()
                    
                    quittances_data = []
                    for p in paiements:
                        mois_noms = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
                                   "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
                        mois_nom = mois_noms[p.mois - 1]
                        
                        statut_emoji = "✅" if p.statut == "paye" else "⏳" if p.statut == "partiel" else "❌"
                        
                        # Calculer la différence de mois par rapport à aujourd'hui
                        date_paiement = datetime(p.annee, p.mois, 1)
                        diff_mois = (date_aujourdhui.year - p.annee) * 12 + (date_aujourdhui.month - p.mois)
                        
                        quittances_data.append({
                            'Période': f"{mois_nom} {p.annee}",
                            'Montant': f"{p.montant:.2f} €",
                            'Statut': f"{statut_emoji} {p.statut.capitalize()}",
                            'Date paiement': p.date_paiement.strftime('%d/%m/%Y') if p.date_paiement else '-',
                            'id': p.id,
                            'mois': p.mois,
                            'annee': p.annee,
                            'paiement': p,
                            'diff_mois': diff_mois
                        })
                    
                    # Trier par les plus proches d'aujourd'hui (diff_mois le plus petit)
                    quittances_data.sort(key=lambda x: abs(x['diff_mois']))
                    
                    # Option pour afficher toutes les quittances
                    if 'afficher_toutes_quittances' not in st.session_state:
                        st.session_state['afficher_toutes_quittances'] = False
                    
                    # Afficher les 3 plus récentes par défaut
                    if not st.session_state['afficher_toutes_quittances']:
                        quittances_affichees = quittances_data[:3]
                        if len(quittances_data) > 3:
                            if st.button(f"📋 Afficher toutes les quittances ({len(quittances_data)} au total)"):
                                st.session_state['afficher_toutes_quittances'] = True
                                st.rerun()
                    else:
                        quittances_affichees = quittances_data
                        if st.button("📋 Afficher uniquement les 3 dernières"):
                            st.session_state['afficher_toutes_quittances'] = False
                            st.rerun()
                    
                    # Affichage et édition des quittances
                    for idx, q in enumerate(quittances_affichees):
                        with st.expander(f"{q['Période']} - {q['Statut']} - {q['Montant']}", expanded=(idx == 0)):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Période:** {q['Période']}")
                                st.write(f"**Montant:** {q['Montant']}")
                            
                            with col2:
                                # Sélection du statut
                                statut_actuel = q['paiement'].statut
                                nouveau_statut = st.selectbox(
                                    "Statut",
                                    ["impaye", "paye", "partiel"],
                                    index=["impaye", "paye", "partiel"].index(statut_actuel),
                                    key=f"statut_{q['id']}"
                                )
                            
                            with col3:
                                # Date de paiement éditable
                                date_actuelle = q['paiement'].date_paiement
                                nouvelle_date = st.date_input(
                                    "Date de paiement",
                                    value=date_actuelle if date_actuelle else None,
                                    key=f"date_{q['id']}"
                                )
                            
                            # Boutons de mise à jour et génération
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("💾 Mettre à jour", key=f"update_{q['id']}"):
                                    # Mettre à jour le paiement
                                    db.update_paiement(
                                        q['id'],
                                        statut=nouveau_statut,
                                        date_paiement=nouvelle_date
                                    )
                                    st.success("✅ Statut mis à jour!")
                                    st.rerun()
                            
                            with col_btn2:
                                # Bouton pour générer/télécharger la quittance
                                if st.button("📄 Générer quittance", key=f"gen_{q['id']}"):
                                    paiement = db.get_paiement_by_id(q['id'])
                                    
                                    # Générer la quittance
                                    fichier_path = qt.generer_quittance_complete(
                                        locataire=locataire,
                                        bail=bail,
                                        chambre=chambre,
                                        appartement=appt_selectionne,
                                        paiement=paiement,
                                        mois=q['mois'],
                                        annee=q['annee']
                                    )
                                    
                                    # Mettre à jour le paiement avec le chemin de la quittance
                                    db.update_paiement(
                                        q['id'],
                                        quittance_generee=True,
                                        chemin_quittance=fichier_path,
                                        date_quittance=date.today()
                                    )
                                    
                                    # Proposer le téléchargement
                                    with open(fichier_path, 'rb') as f:
                                        st.download_button(
                                            label="📥 Télécharger",
                                            data=f.read(),
                                            file_name=os.path.basename(fichier_path),
                                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                            key=f"dl_{q['id']}"
                                        )
                                    st.success(f"✅ Quittance générée : {os.path.basename(fichier_path)}")


# ==================== PARAMÈTRES ====================

elif menu == "⚙️ Paramètres":
    st.markdown("<h1 class='main-header'>⚙️ Paramètres</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📧 Alertes Email", "📊 Statistiques", "ℹ️ À propos"])
    
    with tab1:
        st.subheader("📧 Configuration des Alertes Email")
        
        st.info("Les alertes email sont envoyées automatiquement à partir du 8 de chaque mois pour les loyers impayés.")
        
        email_configured = ea.verifier_config_email()
        
        if email_configured:
            st.success("✅ Configuration email active")
        else:
            st.warning("⚠️ Configuration email non configurée")
            
            st.markdown("""
            Pour activer les alertes email, configurez les variables d'environnement suivantes :
            - `EMAIL_SENDER` : Votre adresse email
            - `EMAIL_PASSWORD` : Mot de passe d'application
            - `SMTP_SERVER` : Serveur SMTP (ex: smtp.gmail.com)
            - `SMTP_PORT` : Port SMTP (ex: 587)
            """)
        
        st.markdown("---")
        
        if st.button("📧 Tester les alertes maintenant"):
            session = db.get_session()
            stats = ea.verifier_et_envoyer_alertes(session)
            
            st.write(f"**Total de paiements à vérifier :** {stats['total']}")
            st.write(f"**Emails envoyés :** {stats['envoyes']}")
            st.write(f"**Erreurs :** {stats['erreurs']}")
            
            if stats.get('details'):
                st.subheader("Détails")
                for detail in stats['details']:
                    if detail['success']:
                        st.success(f"✅ {detail['locataire']} : {detail['message']}")
                    else:
                        st.error(f"❌ {detail['locataire']} : {detail['message']}")
    
    with tab2:
        st.subheader("📊 Statistiques Générales")
        
        stats = db.get_statistiques()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🏢 Nombre d'appartements", stats['nb_appartements'])
            st.metric("🚪 Nombre de chambres", stats['nb_chambres'])
            st.metric("👥 Locataires actifs", stats['nb_locataires_actifs'])
        
        with col2:
            st.metric("💰 Revenus ce mois", f"{stats['revenus_mois_actuel']:.2f} €")
            st.metric("📈 Loyers attendus", f"{stats['loyers_attendus']:.2f} €")
            st.metric("📊 Taux d'occupation", f"{stats['taux_occupation']:.1f}%")
    
    with tab3:
        st.subheader("ℹ️ À propos de Locator")
        
        st.markdown("""
        **Locator** - Application de gestion locative
        
        Version : 1.0.0
        
        Fonctionnalités :
        - 🏢 Gestion des appartements et chambres
        - 👥 Suivi des locataires
        - 💰 Gestion des paiements et loyers
        - 🧾 Génération automatique de quittances
        - 📄 Gestion des factures
        - 📧 Alertes email pour impayés
        - 📊 Tableau de bord et statistiques
        
        ---
        
        © 2025 - Tous droits réservés
        """)
        
        st.markdown("---")
        
        if st.button("🗑️ Réinitialiser la base de données", type="secondary"):
            if st.checkbox("Je confirme vouloir supprimer toutes les données"):
                try:
                    if os.path.exists("locator.db"):
                        os.remove("locator.db")
                    db.init_db()
                    st.success("✅ Base de données réinitialisée")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
