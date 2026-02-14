import sqlite3

conn = sqlite3.connect("bookings.db")
cur = conn.cursor()

cur.execute("ALTER TABLE bookings ADD COLUMN rooms INTEGER DEFAULT 0")
cur.execute("ALTER TABLE bookings ADD COLUMN event_name TEXT")

conn.commit()
conn.close()

print("Migration complete: rooms and event_name columns added.")