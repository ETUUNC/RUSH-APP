import os
import sqlite3
from werkzeug.security import generate_password_hash


def create_db(db_dir=None, default_admin=('admin', 'adminpass')):
    """Create the rush.db in db_dir (or default location) and insert a default admin.

    Returns the full path to the created database.
    """
    if db_dir is None:
        # default to project folder (same directory as this file)
        db_dir = os.path.dirname(__file__)
    DB = os.path.join(db_dir, 'rush.db')
    os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # create tables if not exist
    cur.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        status TEXT,
        payment_status TEXT,
        payment_date TEXT,
        created_at TEXT,
        approved_at TEXT
    )''')
    conn.commit()

    # insert default admin if not exists
    username, password = default_admin
    ph = generate_password_hash(password)
    try:
        cur.execute('INSERT INTO admins (username, password_hash) VALUES (?,?)', (username, ph))
        conn.commit()
        print('Inserted admin:', username)
    except sqlite3.IntegrityError:
        print('Admin already exists:', username)

    print('DB created at', DB)
    conn.close()


if __name__ == '__main__':
    create_db()
