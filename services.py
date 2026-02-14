#services shared logic
from db import connect_db
from pathlib import Path
from datetime import datetime

def view_bookings():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, customer_name, phone, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid, payment_method
    FROM bookings
    ORDER BY start_date
    """)
    rows = cursor.fetchall()
    conn.close()

    print("\nAll Bookings:")
    for r in rows:
        booking_id, name, phone, start_date, end_date, event_type, event_name, rooms, total, paid, method = r
        paid = paid or 0
        total = total or 0
        status = calc_payment_status(total, paid)
        balance = total - paid
        print((booking_id, name, phone, start_date, end_date, event_type, event_name, rooms, total, paid, balance, status, method))
    print()

def get_booking_by_id(booking_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, customer_name, phone, start_date, end_date, event_type, event_name,
               rooms, total_amount, amount_paid, payment_method
        FROM bookings
        WHERE id = ?
    """, (booking_id,))
    row = cur.fetchone()
    conn.close()
    return row

def calc_payment_status(total_amount, amount_paid):
    if amount_paid <= 0:
        return "Unpaid"
    elif amount_paid < total_amount:
        return "Partial"
    else:
        return "Paid"

def compute_balance_status(total_amount, amount_paid):
    balance = float(total_amount) - float(amount_paid)

    if amount_paid <= 0:
        status = "Unpaid"
    elif amount_paid < total_amount:
        status = "Partial"
    else:
        status = "Paid"

    return balance, status

def generate_receipt_txt_for_id(bid):
    booking = get_booking_by_id(int(bid))
    if not booking:
        print("❌ Booking not found.\n")
        return None

    (bid, name, phone, start, end, btype, event_name,
     rooms, total, paid, method) = booking

    name = name.title()
    btype = btype.replace("_", " ").title()
    method = (method or "N/A").title()

    balance = float(total) - float(paid)
    status = calc_payment_status(float(total), float(paid))

    receipt_no = f"PG-{datetime.now().strftime('%Y%m%d')}-{bid:04d}"

    Path("receipts").mkdir(exist_ok=True)
    filename = f"receipts/{receipt_no}.txt"

    lines = [
        "Pelamin Garden Homestay & Event",
        "Lot 1895, Jalan Lenggeng, Kampung Rawa,",
        "71780 Lenggeng, Negeri Sembilan",
        "Tel: 013-4500023, 019-5524789, 011-14789873",
        "Email: pelamingarden@gmail.com",
        "==============================",
        f"Receipt No: {receipt_no}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "------------------------------",
        f"Customer: {name}",
        f"Phone: {phone}",
        f"Type: {btype}",
        f"Event name: {event_name or 'N/A'}",
        f"Dates: {start} to {end}",
        f"Rooms: {rooms}",
        "------------------------------",
        f"Total: RM {float(total):.2f}",
        f"Paid: RM {float(paid):.2f}",
        f"Balance: RM {balance:.2f}",
        f"Status: {status}",
        f"Payment method: {method}",
        "==============================",
    ]

    # Show bank note only if still unpaid/partial
    if balance > 0:
        lines.extend([
            "Note:",
            "Please make payment via online banking / transfer to the following account:",
            "CIMB BANK: 8604701806",
            "RH RENJIS CINTA ENTERPRISE",
            "** Please disregard this notice if payment has been made **",
        ])

    lines.append("Thank you for staying at Pelamin Garden Homestay")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename