import argparse
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

DB = r"c:\Users\TUNÇ\Desktop\rush-app\rush.db"


def list_admins(db_path=DB):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    for row in cur.execute('SELECT id, username FROM admins'):
        print(f"id: {row['id']}, username: {row['username']}")
    conn.close()


def add_admin(username, password, db_path=DB):
    ph = generate_password_hash(password)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', (username, ph))
        conn.commit()
        print('Admin eklendi:', username)
    except sqlite3.IntegrityError:
        print('Bu kullanıcı adı zaten mevcut')
    finally:
        conn.close()


def main():
    p = argparse.ArgumentParser(description='Admin ekle/listesi')
    p.add_argument('--list', action='store_true', help='Mevcut adminleri listele')
    p.add_argument('--username', '-u')
    p.add_argument('--password', '-p', help='Parola (güvenli değil, verilmezse etkileşimli sorulur)')
    args = p.parse_args()

    if args.list:
        list_admins()
        return

    if not args.username:
        print('Kullanıcı adı gerekli (--username)')
        return
    pwd = args.password or getpass('Parola: ')
    add_admin(args.username, pwd)


if __name__ == '__main__':
    main()
