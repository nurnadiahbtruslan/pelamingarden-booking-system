#reports
from db import connect_db
import sqlite3
import csv

def show_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_amount) FROM bookings")
    total_revenue = cursor.fetchone()[0]

    conn.close()

    print("\nBusiness Summary")
    print(f"Total Customers: {total_customers}")
    print(f"Total Revenue: RM {total_revenue}")
    print()

def monthly_report():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT substr(start_date, 1, 7) AS month, SUM(total_amount)
        FROM bookings
        GROUP BY month
        ORDER BY month
    """)

    results = cursor.fetchall()
    conn.close()

    print("\nMonthly Revenue Report")
    for row in results:
        print(f"{row[0]} → RM {row[1]}")
    print()

def export_to_csv():
    conn = sqlite3.connect("bookings.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookings")
    rows = cursor.fetchall()

    with open("bookings_export.csv", mode="w", newline="") as file:
        writer = csv.writer(file)

        # Write header phone, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid, payment_method
        writer.writerow(["ID", "Name", "Phone", "Start Date","End Date", "Event Type", "Event Name", "Rooms Booked", "Total Amount", "Amount Paid", "Payment Method"])

        # Write data
        for row in rows:
            writer.writerow(row)

    conn.close()
    print("Bookings exported successfully to bookings_export.csv")