import sqlite3

conn = sqlite3.connect("bookings.db")
cur = conn.cursor()

# Copy old single date into start_date and end_date
cur.execute("UPDATE bookings SET start_date = date, end_date = date WHERE start_date IS NULL")

# Copy old amount into total_amount (so old data still works)
cur.execute("UPDATE bookings SET total_amount = amount WHERE total_amount IS NULL")

# Ensure amount_paid is not null
cur.execute("UPDATE bookings SET amount_paid = 0 WHERE amount_paid IS NULL")

conn.commit()
conn.close()

print("Backfill complete: old data mapped to new columns.")