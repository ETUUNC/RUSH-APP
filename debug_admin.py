import sqlite3
from werkzeug.security import check_password_hash
DB = r"c:\Users\TUNÇ\Desktop\rush-app\rush.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()
for row in c.execute('SELECT id, username, password_hash FROM admins'):
    print('id:', row['id'], 'username:', row['username'])
    ph = row['password_hash']
    ok = check_password_hash(ph, 'TUNÇ3031')
    print('  hash check for TUNÇ3031 ->', ok)
conn.close()
