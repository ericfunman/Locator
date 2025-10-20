# Locator - Gestion de Location Immobilière

Application web locale pour gérer vos biens locatifs, locataires, paiements et factures.

## Fonctionnalités

- 📊 **Dashboard** : Vue d'ensemble des revenus, taux d'occupation, impayés
- 🏢 **Gestion des appartements** : Ajout/modification d'appartements et chambres (pour colocations)
- 👥 **Gestion des locataires** : Suivi complet des locataires et leurs informations
- 💰 **Suivi des paiements** : Enregistrement des loyers avec suivi des baux et historique des modifications
- 💵 **Historique des loyers** : Traçabilité complète des changements de loyer avec mise à jour automatique des paiements futurs
- 📄 **Gestion des factures** : Stockage et catégorisation des factures
- 🧾 **Génération de quittances** : Création automatique de quittances de loyer au format Word
- 📧 **Envoi de quittances par email** : Envoi automatique des quittances directement aux locataires

## Installation

```bash
pip install -r requirements.txt
```

## Configuration Email

Pour envoyer les quittances par email :

1. Copiez le fichier `.env.example` en `.env`
2. Remplissez vos informations :

```env
SMTP_EMAIL=votre.email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Mot de passe d'application
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM_NAME=Gestion Locative Locator
```

### Pour Gmail :

1. Activez la validation en 2 étapes : https://myaccount.google.com/signinoptions/two-step-verification
2. Créez un mot de passe d'application : https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe dans le fichier `.env`

## Lancement

### Avec le script batch (Windows) :
```bash
StartLocator.bat
```

### Ou manuellement :
```bash
streamlit run app.py
```

L'application sera accessible sur http://localhost:8501

## Structure des données

Les documents sont organisés automatiquement :
- `documents/appartements/[Adresse]/[Année]/Factures/`
- `documents/locataires/[Nom]/[Année]/[Mois]/quittances/`

La base de données SQLite est stockée dans `locator.db`

## Utilisation

### Envoi de quittances par email

1. Allez dans **Quittances**
2. Sélectionnez l'appartement et le locataire
3. Pour chaque période :
   - Cliquez sur **📄 Générer quittance** pour créer le document
   - Cliquez sur **📧 Envoyer par mail** pour l'envoyer au locataire
4. Le statut d'envoi est affiché avec la date et l'heure

### Modification des loyers

1. Allez dans **Baux et Locataires**
2. Développez le bail concerné
3. Cliquez sur **✏️ Modifier le loyer**
4. Entrez le nouveau loyer et la date d'application
5. Tous les paiements futurs seront automatiquement mis à jour

## Sécurité

⚠️ **Important** : Le fichier `.env` contient vos identifiants sensibles et n'est **pas versionné** sur Git.
Conservez-le en lieu sûr et ne le partagez jamais publiquement.
