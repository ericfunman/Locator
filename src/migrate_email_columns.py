"""
Script de migration pour ajouter les colonnes d'envoi d'email aux paiements
"""
import sqlite3
import os

# Chemin vers la base de données
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "locator.db")

def migrate_add_email_columns():
    """Ajoute les colonnes pour l'envoi d'emails si elles n'existent pas"""
    
    if not os.path.exists(DB_PATH):
        print("Base de données introuvable")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si les colonnes existent déjà
        cursor.execute("PRAGMA table_info(paiements)")
        colonnes = [col[1] for col in cursor.fetchall()]
        
        colonnes_a_ajouter = []
        
        if 'quittance_envoyee' not in colonnes:
            colonnes_a_ajouter.append(('quittance_envoyee', 'INTEGER DEFAULT 0'))
        
        if 'date_envoi_quittance' not in colonnes:
            colonnes_a_ajouter.append(('date_envoi_quittance', 'DATETIME'))
        
        if not colonnes_a_ajouter:
            print("✅ Les colonnes existent déjà, aucune migration nécessaire")
            return
        
        # Ajouter les colonnes manquantes
        for nom_colonne, type_colonne in colonnes_a_ajouter:
            sql = f"ALTER TABLE paiements ADD COLUMN {nom_colonne} {type_colonne}"
            print(f"Ajout de la colonne {nom_colonne}...")
            cursor.execute(sql)
        
        conn.commit()
        print(f"✅ Migration réussie ! {len(colonnes_a_ajouter)} colonne(s) ajoutée(s)")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la migration : {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔄 Démarrage de la migration...")
    migrate_add_email_columns()
    print("✅ Migration terminée")
