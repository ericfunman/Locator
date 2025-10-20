import sqlite3

conn = sqlite3.connect('locator.db')
cursor = conn.cursor()

# Structure table chambres
cursor.execute('PRAGMA table_info(chambres)')
print('=== Structure table chambres ===')
for row in cursor.fetchall():
    print(row)

# Structure table locataires
cursor.execute('PRAGMA table_info(locataires)')
print('\n=== Structure table locataires ===')
for row in cursor.fetchall():
    print(row)

# Structure table baux (le nom de la table est 'bails' pas 'baux')
cursor.execute('PRAGMA table_info(bails)')
print('\n=== Structure table bails ===')
for row in cursor.fetchall():
    print(row)

# Liste des tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
print('\n=== Tables disponibles ===')
for row in cursor.fetchall():
    print(row[0])

conn.close()
