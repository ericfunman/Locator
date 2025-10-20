"""
Module de gestion de la base de données
"""

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, date
from .models import Base, Appartement, Chambre, Bail, Locataire, Paiement, Facture, AlerteEmail, HistoriqueLoyer
import os

# Configuration de la base de données
# Utiliser le chemin du fichier actuel pour déterminer le dossier du projet
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "locator.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))


def init_db():
    """Initialise la base de données"""
    Base.metadata.create_all(engine)
    print("Base de données initialisée avec succès")


def migrate_db():
    """Ajoute les nouvelles tables sans supprimer les données existantes"""
    try:
        # Crée uniquement les tables manquantes
        Base.metadata.create_all(engine)
        print("Migration de la base de données effectuée avec succès")
    except Exception as e:
        print(f"Erreur lors de la migration : {e}")
        raise e


def get_session():
    """Retourne une session de base de données"""
    return Session()


# ==================== APPARTEMENTS ====================

def create_appartement(adresse, ville, code_postal, surface, date_acquisition=None, notes=""):
    """Crée un nouvel appartement"""
    session = get_session()
    try:
        appartement = Appartement(
            adresse=adresse,
            ville=ville,
            code_postal=code_postal,
            surface=surface,
            date_acquisition=date_acquisition,
            notes=notes
        )
        session.add(appartement)
        session.commit()
        return appartement
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_appartements():
    """Récupère tous les appartements"""
    session = get_session()
    try:
        return session.query(Appartement).all()
    finally:
        session.close()


def get_appartement_by_id(appartement_id):
    """Récupère un appartement par son ID"""
    session = get_session()
    try:
        return session.query(Appartement).filter(Appartement.id == appartement_id).first()
    finally:
        session.close()


def update_appartement(appartement_id, **kwargs):
    """Met à jour un appartement"""
    session = get_session()
    try:
        appartement = session.query(Appartement).filter(Appartement.id == appartement_id).first()
        if appartement:
            for key, value in kwargs.items():
                if hasattr(appartement, key):
                    setattr(appartement, key, value)
            session.commit()
        return appartement
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_appartement(appartement_id):
    """Supprime un appartement"""
    session = get_session()
    try:
        appartement = session.query(Appartement).filter(Appartement.id == appartement_id).first()
        if appartement:
            session.delete(appartement)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== CHAMBRES ====================

def create_chambre(appartement_id, numero, loyer, charges=0.0, surface=None, est_appartement_complet=False):
    """Crée une nouvelle chambre"""
    session = get_session()
    try:
        chambre = Chambre(
            appartement_id=appartement_id,
            numero=numero,
            loyer=loyer,
            charges=charges,
            surface=surface,
            est_appartement_complet=est_appartement_complet
        )
        session.add(chambre)
        session.commit()
        return chambre
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_chambres_by_appartement(appartement_id):
    """Récupère toutes les chambres d'un appartement"""
    session = get_session()
    try:
        return session.query(Chambre).filter(Chambre.appartement_id == appartement_id).all()
    finally:
        session.close()


def get_chambre_by_id(chambre_id):
    """Récupère une chambre par son ID"""
    session = get_session()
    try:
        return session.query(Chambre).filter(Chambre.id == chambre_id).first()
    finally:
        session.close()


def get_all_chambres():
    """Récupère toutes les chambres"""
    session = get_session()
    try:
        return session.query(Chambre).all()
    finally:
        session.close()


def update_chambre(chambre_id, **kwargs):
    """Met à jour une chambre"""
    session = get_session()
    try:
        chambre = session.query(Chambre).filter(Chambre.id == chambre_id).first()
        if chambre:
            for key, value in kwargs.items():
                if hasattr(chambre, key):
                    setattr(chambre, key, value)
            session.commit()
        return chambre
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_chambre(chambre_id):
    """Supprime une chambre"""
    session = get_session()
    try:
        chambre = session.query(Chambre).filter(Chambre.id == chambre_id).first()
        if chambre:
            session.delete(chambre)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== BAUX ====================

def create_bail(chambre_id, date_debut, loyer_total, charges_total=0.0, date_fin=None, notes=""):
    """Crée un nouveau bail"""
    session = get_session()
    try:
        bail = Bail(
            chambre_id=chambre_id,
            date_debut=date_debut,
            date_fin=date_fin,
            loyer_total=loyer_total,
            charges_total=charges_total,
            actif=True,
            notes=notes
        )
        session.add(bail)
        session.commit()
        
        # Récupérer l'ID avant de fermer la session
        bail_id = bail.id
        
        # Mettre à jour la disponibilité de la chambre
        update_chambre(chambre_id, disponible=False)
        
        return bail_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_bail_by_id(bail_id):
    """Récupère un bail par son ID"""
    session = get_session()
    try:
        return session.query(Bail).filter(Bail.id == bail_id).first()
    finally:
        session.close()


def get_bails_by_chambre(chambre_id):
    """Récupère tous les baux d'une chambre"""
    session = get_session()
    try:
        return session.query(Bail).filter(Bail.chambre_id == chambre_id).all()
    finally:
        session.close()


def get_all_bails(actifs_seulement=False):
    """Récupère tous les baux"""
    session = get_session()
    try:
        query = session.query(Bail)
        if actifs_seulement:
            query = query.filter(Bail.actif == True)
        return query.all()
    finally:
        session.close()


def update_bail(bail_id, **kwargs):
    """Met à jour un bail"""
    session = get_session()
    try:
        bail = session.query(Bail).filter(Bail.id == bail_id).first()
        if bail:
            for key, value in kwargs.items():
                if hasattr(bail, key):
                    setattr(bail, key, value)
            session.commit()
        return bail
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_bail(bail_id):
    """Supprime un bail"""
    session = get_session()
    try:
        bail = session.query(Bail).filter(Bail.id == bail_id).first()
        if bail:
            chambre_id = bail.chambre_id
            session.delete(bail)
            session.commit()
            
            # Libérer la chambre
            update_chambre(chambre_id, disponible=True)
            
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== LOCATAIRES ====================

def create_locataire(nom, email, telephone, date_entree, bail_id=None, depot_garantie=0.0, part_loyer=None, notes=""):
    """Crée un nouveau locataire"""
    session = get_session()
    try:
        locataire = Locataire(
            nom=nom,
            email=email,
            telephone=telephone,
            date_entree=date_entree,
            bail_id=bail_id,
            depot_garantie=depot_garantie,
            part_loyer=part_loyer,
            notes=notes,
            actif=True
        )
        session.add(locataire)
        session.commit()
        
        return locataire
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_locataires(actifs_seulement=False):
    """Récupère tous les locataires"""
    session = get_session()
    try:
        query = session.query(Locataire)
        if actifs_seulement:
            query = query.filter(Locataire.actif == True)
        return query.all()
    finally:
        session.close()


def get_locataire_by_id(locataire_id):
    """Récupère un locataire par son ID"""
    session = get_session()
    try:
        return session.query(Locataire).filter(Locataire.id == locataire_id).first()
    finally:
        session.close()


def update_locataire(locataire_id, **kwargs):
    """Met à jour un locataire"""
    session = get_session()
    try:
        locataire = session.query(Locataire).filter(Locataire.id == locataire_id).first()
        if locataire:
            for key, value in kwargs.items():
                if hasattr(locataire, key):
                    setattr(locataire, key, value)
            
            session.commit()
        
        return locataire
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_locataire(locataire_id):
    """Supprime un locataire"""
    session = get_session()
    try:
        locataire = session.query(Locataire).filter(Locataire.id == locataire_id).first()
        if locataire:
            session.delete(locataire)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== PAIEMENTS ====================

def create_paiement(locataire_id, chambre_id, mois, annee, montant, date_paiement=None, 
                    statut='impaye', mode_paiement=None, notes=""):
    """Crée un nouveau paiement"""
    session = get_session()
    try:
        paiement = Paiement(
            locataire_id=locataire_id,
            chambre_id=chambre_id,
            mois=mois,
            annee=annee,
            montant=montant,
            date_paiement=date_paiement,
            statut=statut,
            mode_paiement=mode_paiement,
            notes=notes
        )
        session.add(paiement)
        session.commit()
        return paiement
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_paiements():
    """Récupère tous les paiements"""
    session = get_session()
    try:
        return session.query(Paiement).all()
    finally:
        session.close()


def get_paiements_by_locataire(locataire_id):
    """Récupère tous les paiements d'un locataire"""
    session = get_session()
    try:
        return session.query(Paiement).filter(Paiement.locataire_id == locataire_id).all()
    finally:
        session.close()


def get_paiement_by_id(paiement_id):
    """Récupère un paiement par son ID"""
    session = get_session()
    try:
        return session.query(Paiement).filter(Paiement.id == paiement_id).first()
    finally:
        session.close()


def get_paiements_impayés():
    """Récupère tous les paiements impayés"""
    session = get_session()
    try:
        return session.query(Paiement).filter(Paiement.statut == 'impaye').all()
    finally:
        session.close()


def get_paiements_by_mois_annee(mois, annee):
    """Récupère tous les paiements pour un mois et une année donnés"""
    session = get_session()
    try:
        return session.query(Paiement).filter(
            and_(Paiement.mois == mois, Paiement.annee == annee)
        ).all()
    finally:
        session.close()


def update_paiement(paiement_id, **kwargs):
    """Met à jour un paiement. Si date_paiement est fournie, le statut passe automatiquement à 'paye'"""
    session = get_session()
    try:
        paiement = session.query(Paiement).filter(Paiement.id == paiement_id).first()
        if paiement:
            # Si date_paiement est fournie et non None, changer automatiquement le statut à 'paye'
            if 'date_paiement' in kwargs and kwargs['date_paiement'] is not None:
                kwargs['statut'] = 'paye'
            # Si date_paiement est None et le statut n'est pas explicitement fourni, passer à 'impaye'
            elif 'date_paiement' in kwargs and kwargs['date_paiement'] is None and 'statut' not in kwargs:
                kwargs['statut'] = 'impaye'
            
            for key, value in kwargs.items():
                if hasattr(paiement, key):
                    setattr(paiement, key, value)
            session.commit()
        return paiement
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_paiement(paiement_id):
    """Supprime un paiement"""
    session = get_session()
    try:
        paiement = session.query(Paiement).filter(Paiement.id == paiement_id).first()
        if paiement:
            session.delete(paiement)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== FACTURES ====================

def create_facture(appartement_id, categorie, montant, date_facture, fournisseur="", 
                   description="", fichier_path="", statut='impaye'):
    """Crée une nouvelle facture"""
    session = get_session()
    try:
        facture = Facture(
            appartement_id=appartement_id,
            categorie=categorie,
            fournisseur=fournisseur,
            montant=montant,
            date_facture=date_facture,
            description=description,
            fichier_path=fichier_path,
            statut=statut
        )
        session.add(facture)
        session.commit()
        return facture
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_all_factures():
    """Récupère toutes les factures"""
    session = get_session()
    try:
        return session.query(Facture).all()
    finally:
        session.close()


def get_factures_by_appartement(appartement_id):
    """Récupère toutes les factures d'un appartement"""
    session = get_session()
    try:
        return session.query(Facture).filter(Facture.appartement_id == appartement_id).all()
    finally:
        session.close()


def get_factures_by_categorie(categorie):
    """Récupère toutes les factures d'une catégorie"""
    session = get_session()
    try:
        return session.query(Facture).filter(Facture.categorie == categorie).all()
    finally:
        session.close()


def update_facture(facture_id, **kwargs):
    """Met à jour une facture"""
    session = get_session()
    try:
        facture = session.query(Facture).filter(Facture.id == facture_id).first()
        if facture:
            for key, value in kwargs.items():
                if hasattr(facture, key):
                    setattr(facture, key, value)
            session.commit()
        return facture
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def delete_facture(facture_id):
    """Supprime une facture"""
    session = get_session()
    try:
        facture = session.query(Facture).filter(Facture.id == facture_id).first()
        if facture:
            session.delete(facture)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# ==================== STATISTIQUES ====================

def get_statistiques():
    """Récupère des statistiques générales"""
    session = get_session()
    try:
        stats = {
            'nb_appartements': session.query(Appartement).count(),
            'nb_chambres': session.query(Chambre).count(),
            'nb_chambres_disponibles': session.query(Chambre).filter(Chambre.disponible == True).count(),
            'nb_locataires_actifs': session.query(Locataire).filter(Locataire.actif == True).count(),
            'nb_paiements_impayés': session.query(Paiement).filter(Paiement.statut == 'impaye').count(),
            'nb_factures_impayées': session.query(Facture).filter(Facture.statut == 'impaye').count(),
        }
        
        # Calcul des revenus mensuels
        mois_actuel = datetime.now().month
        annee_actuelle = datetime.now().year
        
        paiements_mois = session.query(Paiement).filter(
            and_(
                Paiement.mois == mois_actuel,
                Paiement.annee == annee_actuelle,
                Paiement.statut == 'paye'
            )
        ).all()
        
        stats['revenus_mois_actuel'] = sum([p.montant for p in paiements_mois])
        
        # Montant total des loyers attendus ce mois
        chambres_occupees = session.query(Chambre).filter(Chambre.disponible == False).all()
        stats['loyers_attendus'] = sum([c.loyer + c.charges for c in chambres_occupees])
        
        # Taux d'occupation
        if stats['nb_chambres'] > 0:
            stats['taux_occupation'] = ((stats['nb_chambres'] - stats['nb_chambres_disponibles']) / stats['nb_chambres']) * 100
        else:
            stats['taux_occupation'] = 0
        
        return stats
    finally:
        session.close()


# ==================== HISTORIQUE DES LOYERS ====================

def create_historique_loyer(bail_id, ancien_loyer, nouveau_loyer, anciennes_charges, nouvelles_charges, date_application, notes=""):
    """Crée un historique de changement de loyer"""
    session = get_session()
    try:
        historique = HistoriqueLoyer(
            bail_id=bail_id,
            ancien_loyer=ancien_loyer,
            nouveau_loyer=nouveau_loyer,
            anciennes_charges=anciennes_charges,
            nouvelles_charges=nouvelles_charges,
            date_application=date_application,
            notes=notes
        )
        session.add(historique)
        session.commit()
        return historique
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def get_historique_by_bail(bail_id):
    """Récupère l'historique des changements de loyer pour un bail"""
    session = get_session()
    try:
        historiques = session.query(HistoriqueLoyer).filter(
            HistoriqueLoyer.bail_id == bail_id
        ).order_by(HistoriqueLoyer.date_application.desc()).all()
        return historiques
    finally:
        session.close()


def update_bail_loyer(bail_id, nouveau_loyer, nouvelles_charges, date_application, notes=""):
    """
    Met à jour le loyer d'un bail et crée un historique.
    Met également à jour tous les paiements futurs à partir de la date d'application.
    """
    session = get_session()
    try:
        # Récupérer le bail
        bail = session.query(Bail).filter(Bail.id == bail_id).first()
        if not bail:
            raise ValueError("Bail introuvable")
        
        # Sauvegarder les anciennes valeurs
        ancien_loyer = bail.loyer_total
        anciennes_charges = bail.charges_total
        
        # Créer l'historique
        historique = HistoriqueLoyer(
            bail_id=bail_id,
            ancien_loyer=ancien_loyer,
            nouveau_loyer=nouveau_loyer,
            anciennes_charges=anciennes_charges,
            nouvelles_charges=nouvelles_charges,
            date_application=date_application,
            notes=notes
        )
        session.add(historique)
        
        # Mettre à jour le bail
        bail.loyer_total = nouveau_loyer
        bail.charges_total = nouvelles_charges
        
        # Mettre à jour les paiements futurs
        annee_application = date_application.year
        mois_application = date_application.month
        
        # Calculer le nouveau montant total
        nouveau_montant_total = nouveau_loyer + nouvelles_charges
        
        # Récupérer tous les locataires du bail
        locataires = session.query(Locataire).filter(Locataire.bail_id == bail_id).all()
        
        # Mettre à jour les paiements pour chaque locataire
        nb_locataires = len(locataires)
        for locataire in locataires:
            # Calculer le nouveau montant pour ce locataire
            if locataire.part_loyer is not None:
                # Si une part est définie, calculer la proportion et l'appliquer au nouveau total
                ancien_total = ancien_loyer + anciennes_charges
                if ancien_total > 0:
                    proportion = locataire.part_loyer / ancien_total
                    nouveau_montant = nouveau_montant_total * proportion
                else:
                    # Si pas de loyer précédent, diviser équitablement
                    nouveau_montant = nouveau_montant_total / nb_locataires if nb_locataires > 0 else nouveau_montant_total
                
                # Mettre à jour la part_loyer du locataire
                locataire.part_loyer = nouveau_montant
            else:
                # Si pas de part définie, diviser équitablement
                nouveau_montant = nouveau_montant_total / nb_locataires if nb_locataires > 0 else nouveau_montant_total
            
            # Mettre à jour les paiements futurs (>= date d'application)
            paiements_futurs = session.query(Paiement).filter(
                and_(
                    Paiement.locataire_id == locataire.id,
                    or_(
                        Paiement.annee > annee_application,
                        and_(
                            Paiement.annee == annee_application,
                            Paiement.mois >= mois_application
                        )
                    )
                )
            ).all()
            
            for paiement in paiements_futurs:
                paiement.montant = nouveau_montant
        
        session.commit()
        return bail, len([p for loc in locataires for p in session.query(Paiement).filter(
            and_(
                Paiement.locataire_id == loc.id,
                or_(
                    Paiement.annee > annee_application,
                    and_(
                        Paiement.annee == annee_application,
                        Paiement.mois >= mois_application
                    )
                )
            )
        ).all()])
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
