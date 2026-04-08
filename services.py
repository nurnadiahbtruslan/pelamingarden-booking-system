#services shared logic
from db import connect_db
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

from reportlab.platypus import Image

def generate_receipt_pdf(booking):
    today = datetime.today().strftime("%Y-%m-%d")
    file_name = f"{today}_receipt_{booking['customer_name']}_{booking['id']}.pdf"

    c = canvas.Canvas(file_name, pagesize=letter)
    
    c.drawImage("logo.png", 50, 700, width=70, height=70)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(130, 750, "Pelamin Garden Homestay")

    c.setFont("Helvetica", 10)
    c.drawString(130, 730, "Lot 1895, Jalan Lenggeng, Kampung Rawa,")
    c.drawString(130, 715, "71780 Lenggeng, Negeri Sembilan")
    c.drawString(130, 700, "Phone: 013-4500023, 019-5524789, 011-14789873")

    c.line(50, 675, 550, 675)

    y = 650
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "BOOKING RECEIPT")
    y-= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Customer: {booking['customer_name']}")
    y-= 20

    c.drawString(50, y, f"Phone: {booking['phone']}")
    y-= 20

    c.drawString(50, y, f"Event type: {booking['event_type']}")
    y-= 20

    c.drawString(50, y, f"Event name: {booking['event_name']}")
    y-= 20

    c.drawString(50, y, f"Date: {booking['start_date']} - {booking['end_date']}")
    y-= 20

    c.drawString(50, y, f"Rooms: {booking['rooms']}")
    y-= 20

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, f"Total: RM{booking['total_amount']}")
    y-= 20

    c.drawString(50, y, f"Amount Paid: RM{booking['amount_paid']}")
    y-= 20

    c.drawString(50, y, f"Balance: RM{booking['balance']}")
    y-= 20

    c.drawString(50, y, f"Status: {booking['status']}")
    
    y = 130
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Note:")
    y-= 15
    c.drawString(50, y, "Please make payment via online banking/transfer to following account.")
    y-= 15
    c.drawString(50, y, "CIMB BANK 8604701806")
    y-= 15
    c.drawString(50, y, "RH RENJIS CINTA ENTERPRISE")
    y-= 15
    c.drawString(50, y, "**Please disregard this notice if payment have been made")
    y-= 25
    c.drawString(50, y, "Thank You for staying at Pelamin Garden Homestay")

    c.save()

    return file_name

    