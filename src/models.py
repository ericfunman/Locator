"""
Modèles de base de données pour Locator
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()


class Appartement(Base):
    """Modèle pour les appartements"""
    __tablename__ = 'appartements'
    
    id = Column(Integer, primary_key=True)
    adresse = Column(String(200), nullable=False)
    ville = Column(String(100), nullable=False)
    code_postal = Column(String(10), nullable=False)
    surface = Column(Float, nullable=False)  # en m²
    date_acquisition = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    chambres = relationship("Chambre", back_populates="appartement", cascade="all, delete-orphan")
    factures = relationship("Facture", back_populates="appartement", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Appartement(adresse='{self.adresse}')>"


class Chambre(Base):
    """Modèle pour les chambres (pour gérer les colocations)"""
    __tablename__ = 'chambres'
    
    id = Column(Integer, primary_key=True)
    appartement_id = Column(Integer, ForeignKey('appartements.id'), nullable=False)
    numero = Column(String(50), nullable=False)  # ex: "Chambre 1", "Studio", "Appartement complet", etc.
    loyer = Column(Float, nullable=False)
    charges = Column(Float, default=0.0)
    surface = Column(Float)  # surface de la chambre si applicable
    est_appartement_complet = Column(Boolean, default=False)  # True si c'est l'appartement entier
    disponible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    appartement = relationship("Appartement", back_populates="chambres")
    bails = relationship("Bail", back_populates="chambre", cascade="all, delete-orphan")
    paiements = relationship("Paiement", back_populates="chambre", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chambre(numero='{self.numero}', loyer={self.loyer})>"


class Bail(Base):
    """Modèle pour les baux (contrats de location)"""
    __tablename__ = 'bails'
    
    id = Column(Integer, primary_key=True)
    chambre_id = Column(Integer, ForeignKey('chambres.id'), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    loyer_total = Column(Float, nullable=False)
    charges_total = Column(Float, default=0.0)
    actif = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    chambre = relationship("Chambre", back_populates="bails")
    locataires = relationship("Locataire", back_populates="bail")
    historique_loyers = relationship("HistoriqueLoyer", back_populates="bail", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bail(chambre_id={self.chambre_id}, actif={self.actif})>"


class HistoriqueLoyer(Base):
    """Modèle pour l'historique des changements de loyer"""
    __tablename__ = 'historique_loyers'
    
    id = Column(Integer, primary_key=True)
    bail_id = Column(Integer, ForeignKey('bails.id'), nullable=False)
    ancien_loyer = Column(Float, nullable=False)
    nouveau_loyer = Column(Float, nullable=False)
    anciennes_charges = Column(Float, default=0.0)
    nouvelles_charges = Column(Float, default=0.0)
    date_changement = Column(DateTime, default=datetime.now)  # Date de l'enregistrement du changement
    date_application = Column(Date, nullable=False)  # Date à partir de laquelle le nouveau loyer s'applique
    notes = Column(Text)
    
    # Relations
    bail = relationship("Bail", back_populates="historique_loyers")
    
    def __repr__(self):
        return f"<HistoriqueLoyer(bail_id={self.bail_id}, ancien={self.ancien_loyer}, nouveau={self.nouveau_loyer})>"


class Locataire(Base):
    """Modèle pour les locataires"""
    __tablename__ = 'locataires'
    
    id = Column(Integer, primary_key=True)
    bail_id = Column(Integer, ForeignKey('bails.id'), nullable=True)
    nom = Column(String(200), nullable=False)  # Contient maintenant le nom complet
    email = Column(String(150))
    telephone = Column(String(20))
    date_entree = Column(Date, nullable=False)
    date_sortie = Column(Date, nullable=True)
    part_loyer = Column(Float, nullable=True)  # Part individuelle du loyer (pour colocation)
    depot_garantie = Column(Float, default=0.0)  # Caution versée par le locataire
    actif = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    bail = relationship("Bail", back_populates="locataires")
    paiements = relationship("Paiement", back_populates="locataire", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Locataire(nom='{self.nom}')>"
    
    @property
    def nom_complet(self):
        return self.nom


class Paiement(Base):
    """Modèle pour les paiements de loyer"""
    __tablename__ = 'paiements'
    
    id = Column(Integer, primary_key=True)
    locataire_id = Column(Integer, ForeignKey('locataires.id'), nullable=False)
    chambre_id = Column(Integer, ForeignKey('chambres.id'), nullable=False)
    mois = Column(Integer, nullable=False)  # 1-12
    annee = Column(Integer, nullable=False)
    montant = Column(Float, nullable=False)
    date_paiement = Column(Date)
    statut = Column(String(20), default='impaye')  # 'paye', 'impaye', 'partiel'
    mode_paiement = Column(String(50))  # 'virement', 'cheque', 'especes'
    notes = Column(Text)
    quittance_generee = Column(Boolean, default=False)
    date_quittance = Column(Date, nullable=True)  # Date de génération de la quittance
    chemin_quittance = Column(String(500), nullable=True)  # Chemin vers le fichier de quittance généré
    quittance_envoyee = Column(Boolean, default=False)  # Si la quittance a été envoyée par email
    date_envoi_quittance = Column(DateTime, nullable=True)  # Date d'envoi de la quittance par email
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    locataire = relationship("Locataire", back_populates="paiements")
    chambre = relationship("Chambre", back_populates="paiements")
    
    def __repr__(self):
        return f"<Paiement(locataire_id={self.locataire_id}, mois={self.mois}/{self.annee}, statut='{self.statut}')>"


class Facture(Base):
    """Modèle pour les factures"""
    __tablename__ = 'factures'
    
    id = Column(Integer, primary_key=True)
    appartement_id = Column(Integer, ForeignKey('appartements.id'), nullable=False)
    categorie = Column(String(50), nullable=False)  # 'travaux', 'electricite', 'eau', 'gaz', 'assurance', 'autre'
    fournisseur = Column(String(150))
    montant = Column(Float, nullable=False)
    date_facture = Column(Date, nullable=False)
    date_paiement = Column(Date)
    statut = Column(String(20), default='impaye')  # 'paye', 'impaye'
    description = Column(Text)
    fichier_path = Column(String(500))  # chemin vers le fichier PDF/image
    created_at = Column(DateTime, default=datetime.now)
    
    # Relations
    appartement = relationship("Appartement", back_populates="factures")
    
    def __repr__(self):
        return f"<Facture(categorie='{self.categorie}', montant={self.montant})>"


class AlerteEmail(Base):
    """Modèle pour suivre les alertes email envoyées"""
    __tablename__ = 'alertes_email'
    
    id = Column(Integer, primary_key=True)
    locataire_id = Column(Integer, ForeignKey('locataires.id'), nullable=False)
    paiement_id = Column(Integer, ForeignKey('paiements.id'), nullable=False)
    date_envoi = Column(DateTime, default=datetime.now)
    statut = Column(String(20))  # 'envoye', 'erreur'
    message_erreur = Column(Text)
    
    def __repr__(self):
        return f"<AlerteEmail(locataire_id={self.locataire_id}, date_envoi={self.date_envoi})>"
