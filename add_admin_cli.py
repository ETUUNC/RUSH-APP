#!/usr/bin/env python
import sys
import sqlite3
from werkzeug.security import generate_password_hash

DB = r"c:\Users\TUNÇ\Desktop\rush-app\rush.db"

def main():
    if len(sys.argv) < 3:
        print("Usage: add_admin_cli.py USERNAME PASSWORD")
        sys.exit(1)
    username = sys.argv[1]
    password = sys.argv[2]
    ph = generate_password_hash(password)
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO admins (username,password_hash) VALUES (?,?)', (username, ph))
        conn.commit()
        print('Admin created:', username)
    except sqlite3.IntegrityError:
        print('Username already exists')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
