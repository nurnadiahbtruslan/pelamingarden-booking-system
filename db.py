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

def fetch_all_bookings():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, customer_name, phone, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid
        FROM bookings
        ORDER BY id ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
    
def fetch_total_revenue():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total_amount) FROM bookings")
    total = cur.fetchone()[0]
    conn.close()
    return total or 0

def insert_booking(data):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO bookings (
                customer_name,
                phone,
                event_type,
                event_name, 
                start_date, 
                end_date, 
                rooms,
                total_amount,
                amount_paid
            )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)          
    """, (
        data["customer_name"],
        data["phone"],
        data["event_type"],
        data["event_name"],
        data["start_date"],
        data["end_date"],
        data["rooms"],
        data["total_amount"],
        data["amount_paid"]
    ))
    conn.commit()
    conn.close()

def get_overlapping_bookings(start_date, end_date):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT event_type, rooms FROM bookings
        WHERE start_date <= ? AND end_date >= ?
    """, (end_date, start_date))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_booking_by_id(booking_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, customer_name, phone, event_type, event_name, start_date, end_date, rooms, total_amount, amount_paid
        FROM bookings
        WHERE id = ?
    """, (booking_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "id": row[0],
        "customer_name": row[1],
        "phone": row[2],
        "event_type": row[3],
        "event_name": row[4],
        "start_date": row[5],
        "end_date": row[6],
        "rooms": row[7],
        "total_amount": row[8],
        "amount_paid": row[9]
    }

def update_payment_db(booking_id, amount_paid):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE bookings SET amount_paid = ?
        WHERE id = ?         
    """, (amount_paid, booking_id))
    conn.commit()
    conn.close()

def delete_booking_db(booking_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM bookings
        WHERE id = ?         
    """, (booking_id,))
    conn.commit()
    conn.close()