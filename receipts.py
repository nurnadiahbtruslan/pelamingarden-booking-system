# receipts.py
from db import connect_db
from pathlib import Path
from datetime import datetime
from services import view_bookings, generate_receipt_txt_for_id

def generate_receipt_txt():
    print("\nGenerate Receipt (TXT)")
    view_bookings()

    booking_id = input("Enter booking ID: ").strip()
    if not booking_id.isdigit():
        print("❌ Invalid booking ID.\n")
        return

    filename = generate_receipt_txt_for_id(int(booking_id))
    if filename:
        print(f"\n✅ Receipt created: {filename}\n")