"""
Module de gestion des fichiers et répertoires
"""

import os
from pathlib import Path
import shutil


BASE_DIR = "documents"
APPARTEMENTS_DIR = os.path.join(BASE_DIR, "appartements")
LOCATAIRES_DIR = os.path.join(BASE_DIR, "locataires")


def init_directories():
    """Initialise les répertoires de base"""
    os.makedirs(APPARTEMENTS_DIR, exist_ok=True)
    os.makedirs(LOCATAIRES_DIR, exist_ok=True)
    print(f"Répertoires initialisés : {BASE_DIR}")


def get_appartement_dir(adresse, annee):
    """Retourne le chemin du répertoire pour un appartement et une année donnée"""
    # Nettoyer l'adresse pour le nom de dossier
    safe_adresse = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in adresse)
    safe_adresse = safe_adresse.replace(' ', '_')
    
    path = os.path.join(APPARTEMENTS_DIR, safe_adresse, str(annee), "Factures")
    os.makedirs(path, exist_ok=True)
    return path


def get_locataire_dir(nom, annee, mois):
    """Retourne le chemin du répertoire pour un locataire, année et mois donnés"""
    # Nettoyer le nom pour le nom de dossier
    safe_nom = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in nom)
    safe_nom = safe_nom.replace(' ', '_')
    
    # Nom du mois
    mois_noms = [
        "Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"
    ]
    mois_nom = mois_noms[mois - 1] if 1 <= mois <= 12 else str(mois)
    
    path = os.path.join(LOCATAIRES_DIR, safe_nom, str(annee), mois_nom, "quittances")
    os.makedirs(path, exist_ok=True)
    return path


def save_facture_file(source_file, appartement_adresse, annee, filename=None):
    """
    Sauvegarde un fichier de facture dans le répertoire approprié
    
    Args:
        source_file: Chemin du fichier source ou objet file-like (de Streamlit)
        appartement_adresse: Adresse de l'appartement
        annee: Année de la facture
        filename: Nom du fichier de destination (optionnel)
    
    Returns:
        Chemin complet du fichier sauvegardé
    """
    dest_dir = get_appartement_dir(appartement_adresse, annee)
    
    # Déterminer le nom du fichier
    if filename is None:
        if hasattr(source_file, 'name'):
            filename = source_file.name
        else:
            filename = os.path.basename(source_file)
    
    dest_path = os.path.join(dest_dir, filename)
    
    # Copier le fichier
    if hasattr(source_file, 'read'):
        # C'est un objet file-like (Streamlit UploadedFile)
        with open(dest_path, 'wb') as f:
            f.write(source_file.read())
    else:
        # C'est un chemin de fichier
        shutil.copy2(source_file, dest_path)
    
    return dest_path


def save_quittance_file(file_path, nom, annee, mois):
    """
    Sauvegarde une quittance dans le répertoire approprié
    
    Args:
        file_path: Chemin du fichier de quittance généré
        nom: Nom complet du locataire
        annee: Année de la quittance
        mois: Mois de la quittance
    
    Returns:
        Chemin complet du fichier sauvegardé
    """
    dest_dir = get_locataire_dir(nom, annee, mois)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(dest_dir, filename)
    
    # Copier le fichier
    shutil.copy2(file_path, dest_path)
    
    return dest_path


def get_factures_files(appartement_adresse, annee=None):
    """
    Récupère la liste des fichiers de factures pour un appartement
    
    Args:
        appartement_adresse: Adresse de l'appartement
        annee: Année spécifique (optionnel, sinon toutes les années)
    
    Returns:
        Liste des chemins de fichiers
    """
    safe_adresse = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in appartement_adresse)
    safe_adresse = safe_adresse.replace(' ', '_')
    
    files = []
    base_path = os.path.join(APPARTEMENTS_DIR, safe_adresse)
    
    if not os.path.exists(base_path):
        return files
    
    if annee:
        factures_dir = os.path.join(base_path, str(annee), "Factures")
        if os.path.exists(factures_dir):
            files = [os.path.join(factures_dir, f) for f in os.listdir(factures_dir) 
                    if os.path.isfile(os.path.join(factures_dir, f))]
    else:
        # Toutes les années
        for year_dir in os.listdir(base_path):
            factures_dir = os.path.join(base_path, year_dir, "Factures")
            if os.path.exists(factures_dir):
                files.extend([os.path.join(factures_dir, f) for f in os.listdir(factures_dir) 
                            if os.path.isfile(os.path.join(factures_dir, f))])
    
    return files


def get_quittances_files(nom, prenom, annee=None, mois=None):
    """
    Récupère la liste des quittances pour un locataire
    
    Args:
        nom: Nom du locataire
        prenom: Prénom du locataire
        annee: Année spécifique (optionnel)
        mois: Mois spécifique (optionnel)
    
    Returns:
        Liste des chemins de fichiers
    """
    safe_nom = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in f"{nom}_{prenom}")
    safe_nom = safe_nom.replace(' ', '_')
    
    files = []
    base_path = os.path.join(LOCATAIRES_DIR, safe_nom)
    
    if not os.path.exists(base_path):
        return files
    
    mois_noms = [
        "Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre"
    ]
    
    if annee and mois:
        mois_nom = mois_noms[mois - 1] if 1 <= mois <= 12 else str(mois)
        quittances_dir = os.path.join(base_path, str(annee), mois_nom, "quittances")
        if os.path.exists(quittances_dir):
            files = [os.path.join(quittances_dir, f) for f in os.listdir(quittances_dir) 
                    if os.path.isfile(os.path.join(quittances_dir, f))]
    elif annee:
        year_path = os.path.join(base_path, str(annee))
        if os.path.exists(year_path):
            for month_dir in os.listdir(year_path):
                quittances_dir = os.path.join(year_path, month_dir, "quittances")
                if os.path.exists(quittances_dir):
                    files.extend([os.path.join(quittances_dir, f) for f in os.listdir(quittances_dir) 
                                if os.path.isfile(os.path.join(quittances_dir, f))])
    else:
        # Toutes les années et tous les mois
        for year_dir in os.listdir(base_path):
            year_path = os.path.join(base_path, year_dir)
            if os.path.isdir(year_path):
                for month_dir in os.listdir(year_path):
                    quittances_dir = os.path.join(year_path, month_dir, "quittances")
                    if os.path.exists(quittances_dir):
                        files.extend([os.path.join(quittances_dir, f) for f in os.listdir(quittances_dir) 
                                    if os.path.isfile(os.path.join(quittances_dir, f))])
    
    return files


def delete_file(file_path):
    """Supprime un fichier"""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
