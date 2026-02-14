# db.py
import sqlite3

# db.py
import sqlite3

DB_PATH = "bookings.db"

def connect_db():
    return sqlite3.connect(DB_PATH)

def fetch_one(sql, params=()):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()

def execute(sql, params=()):
    with connect_db() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        return cur.lastrowid

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        phone TEXT,
        start_date TEXT,
        end_date TEXT,
        event_type TEXT,
        event_name,
        rooms INTEGER DEFAULT 0,
        total_amount REAL,
        amount_paid REAL DEFAULT 0,
        payment_method TEXT
    )
    """)
    conn.commit()
    conn.close()