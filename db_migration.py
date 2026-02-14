import sqlite3

conn = sqlite3.connect("bookings.db")
cur = conn.cursor()

# 1) Add new date range columns
cur.execute("ALTER TABLE bookings ADD COLUMN start_date TEXT")
cur.execute("ALTER TABLE bookings ADD COLUMN end_date TEXT")

# 2) Add payment tracking columns
cur.execute("ALTER TABLE bookings ADD COLUMN total_amount REAL")
cur.execute("ALTER TABLE bookings ADD COLUMN amount_paid REAL DEFAULT 0")
cur.execute("ALTER TABLE bookings ADD COLUMN payment_method TEXT")

conn.commit()
conn.close()

print("Migration complete: new columns added.")