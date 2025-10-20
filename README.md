# Locator - Gestion de Location Immobilière

Application web locale pour gérer vos biens locatifs, locataires, paiements et factures.

## Fonctionnalités

- 📊 **Dashboard** : Vue d'ensemble des revenus, taux d'occupation, impayés
- 🏢 **Gestion des appartements** : Ajout/modification d'appartements et chambres (pour colocations)
- 👥 **Gestion des locataires** : Suivi complet des locataires et leurs informations
- 💰 **Suivi des paiements** : Enregistrement des loyers avec alertes pour impayés
- 📄 **Gestion des factures** : Stockage et catégorisation des factures
- 🧾 **Génération de quittances** : Création automatique de quittances de loyer
- 📧 **Alertes email** : Notifications automatiques pour les loyers impayés (à partir du 8 du mois)

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

L'application sera accessible sur http://localhost:8501

## Structure des données

Les documents sont organisés automatiquement :
- `documents/appartements/[Adresse]/[Année]/Factures/`
- `documents/locataires/[Nom_Prenom]/[Année]/[Mois]/quittances/`

La base de données SQLite est stockée dans `locator.db`

## Configuration

Pour activer les alertes email, configurez les variables d'environnement :
- `EMAIL_SENDER` : Votre adresse email
- `EMAIL_PASSWORD` : Mot de passe de l'application
- `SMTP_SERVER` : Serveur SMTP (ex: smtp.gmail.com)
- `SMTP_PORT` : Port SMTP (ex: 587)
