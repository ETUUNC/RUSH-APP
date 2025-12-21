import sqlite3
import getpass
from werkzeug.security import generate_password_hash

DB = r"c:\Users\TUNÇ\Desktop\rush-app\rush.db"

def main():
    username = input('Admin kullanıcı adı: ').strip()
    if not username:
        print('Kullanıcı adı boş olamaz')
        return
    password = getpass.getpass('Parola: ')
    password2 = getpass.getpass('Parola tekrar: ')
    if password != password2:
        print('Parolalar eşleşmiyor')
        return
    ph = generate_password_hash(password)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', (username, ph))
        conn.commit()
        print('Admin oluşturuldu:', username)
    except sqlite3.IntegrityError:
        print('Bu kullanıcı adı zaten mevcut')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
