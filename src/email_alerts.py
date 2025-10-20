"""
Module d'envoi d'alertes email pour les loyers impayés
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def get_email_config():
    """Récupère la configuration email depuis les variables d'environnement"""
    return {
        'sender': os.getenv('SMTP_EMAIL', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'from_name': os.getenv('SMTP_FROM_NAME', 'Gestion Locative')
    }


def verifier_config_email():
    """Vérifie si la configuration email est complète"""
    config = get_email_config()
    return bool(config['sender'] and config['password'])


def envoyer_alerte_loyer_impaye(locataire, paiement, chambre, appartement):
    """
    Envoie un email d'alerte pour un loyer impayé
    
    Args:
        locataire: Objet Locataire
        paiement: Objet Paiement
        chambre: Objet Chambre
        appartement: Objet Appartement
    
    Returns:
        tuple (success: bool, error_message: str)
    """
    if not locataire.email:
        return False, "Le locataire n'a pas d'adresse email"
    
    config = get_email_config()
    
    if not config['sender'] or not config['password']:
        return False, "Configuration email incomplète"
    
    try:
        # Noms des mois
        mois_noms = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        mois_nom = mois_noms[paiement.mois - 1] if 1 <= paiement.mois <= 12 else str(paiement.mois)
        
        # Créer le message
        message = MIMEMultipart()
        message['From'] = config['sender']
        message['To'] = locataire.email
        message['Subject'] = f'Rappel - Loyer impayé pour {mois_nom} {paiement.annee}'
        
        # Corps du message
        body = f"""
Bonjour {locataire.nom},

Nous vous informons que le loyer du mois de {mois_nom} {paiement.annee} n'a pas encore été réglé.

Détails :
- Appartement : {appartement.adresse}, {appartement.code_postal} {appartement.ville}
- Chambre : {chambre.numero}
- Montant dû : {paiement.montant:.2f} €
- Période : {mois_nom} {paiement.annee}

Nous vous remercions de bien vouloir régulariser votre situation dans les plus brefs délais.

Cordialement,

[Votre nom]
        """
        
        message.attach(MIMEText(body, 'plain'))
        
        # Connexion au serveur SMTP
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['sender'], config['password'])
        
        # Envoi du message
        server.send_message(message)
        server.quit()
        
        return True, "Email envoyé avec succès"
    
    except Exception as e:
        return False, str(e)


def verifier_et_envoyer_alertes(session):
    """
    Vérifie tous les paiements impayés et envoie des alertes si nécessaire
    À exécuter quotidiennement à partir du 8 du mois
    
    Args:
        session: Session de base de données
    
    Returns:
        dict avec les statistiques d'envoi
    """
    from .database import get_paiements_impayés, get_locataire_by_id, get_chambre_by_id
    from .models import Appartement, AlerteEmail
    
    # Vérifier si on est après le 8 du mois
    jour_actuel = datetime.now().day
    mois_actuel = datetime.now().month
    annee_actuelle = datetime.now().year
    
    if jour_actuel < 8:
        return {'total': 0, 'envoyes': 0, 'erreurs': 0, 'message': 'Pas encore le 8 du mois'}
    
    stats = {
        'total': 0,
        'envoyes': 0,
        'erreurs': 0,
        'details': []
    }
    
    # Récupérer tous les paiements impayés
    paiements_impayés = get_paiements_impayés()
    
    for paiement in paiements_impayés:
        # Ne traiter que les paiements du mois en cours ou précédents
        if paiement.annee > annee_actuelle or (paiement.annee == annee_actuelle and paiement.mois > mois_actuel):
            continue
        
        stats['total'] += 1
        
        # Vérifier si une alerte a déjà été envoyée ce mois
        alerte_existe = session.query(AlerteEmail).filter(
            AlerteEmail.paiement_id == paiement.id,
            AlerteEmail.date_envoi >= datetime(annee_actuelle, mois_actuel, 1)
        ).first()
        
        if alerte_existe:
            continue
        
        # Récupérer les informations
        locataire = get_locataire_by_id(paiement.locataire_id)
        chambre = get_chambre_by_id(paiement.chambre_id)
        appartement = session.query(Appartement).filter(Appartement.id == chambre.appartement_id).first()
        
        # Envoyer l'alerte
        success, message = envoyer_alerte_loyer_impaye(locataire, paiement, chambre, appartement)
        
        # Enregistrer l'alerte
        alerte = AlerteEmail(
            locataire_id=locataire.id,
            paiement_id=paiement.id,
            statut='envoye' if success else 'erreur',
            message_erreur=message if not success else None
        )
        session.add(alerte)
        
        if success:
            stats['envoyes'] += 1
        else:
            stats['erreurs'] += 1
        
        stats['details'].append({
            'locataire': locataire.nom,
            'success': success,
            'message': message
        })
    
    session.commit()
    
    return stats


def envoyer_quittance_email(locataire, paiement, chambre, appartement, chemin_quittance):
    """
    Envoie la quittance par email au locataire
    
    Args:
        locataire: Objet Locataire
        paiement: Objet Paiement
        chambre: Objet Chambre
        appartement: Objet Appartement
        chemin_quittance: Chemin vers le fichier de quittance
    
    Returns:
        tuple (success: bool, error_message: str)
    """
    if not locataire.email:
        return False, "Le locataire n'a pas d'adresse email"
    
    if not os.path.exists(chemin_quittance):
        return False, "Le fichier de quittance n'existe pas"
    
    config = get_email_config()
    
    if not config['sender'] or not config['password']:
        return False, "Configuration email incomplète. Vérifiez le fichier .env"
    
    try:
        # Noms des mois
        mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                     'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        
        mois_nom = mois_noms[paiement.mois]
        
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = f"{config['from_name']} <{config['sender']}>"
        msg['To'] = locataire.email
        msg['Subject'] = f"Quittance de loyer - {mois_nom} {paiement.annee}"
        
        # Corps du message
        corps = f"""
Bonjour {locataire.nom},

Veuillez trouver ci-joint votre quittance de loyer pour le mois de {mois_nom} {paiement.annee}.

Détails :
- Adresse : {appartement.adresse}, {appartement.code_postal} {appartement.ville}
- Logement : {chambre.numero}
- Montant : {paiement.montant:.2f} €
- Période : {mois_nom} {paiement.annee}

Cordialement,
{config['from_name']}

---
Ceci est un message automatique, merci de ne pas y répondre directement.
"""
        
        msg.attach(MIMEText(corps, 'plain', 'utf-8'))
        
        # Ajout de la pièce jointe
        nom_fichier = os.path.basename(chemin_quittance)
        
        with open(chemin_quittance, 'rb') as f:
            piece_jointe = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
            piece_jointe.set_payload(f.read())
            encoders.encode_base64(piece_jointe)
            piece_jointe.add_header('Content-Disposition', f'attachment; filename="{nom_fichier}"')
            msg.attach(piece_jointe)
        
        # Envoi de l'email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender'], config['password'])
            server.send_message(msg)
        
        return True, "Email envoyé avec succès"
    
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification SMTP. Vérifiez vos identifiants dans le fichier .env"
    except smtplib.SMTPException as e:
        return False, f"Erreur SMTP: {str(e)}"
    except Exception as e:
        return False, f"Erreur lors de l'envoi de l'email: {str(e)}"
