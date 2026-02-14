# payments.py
from db import connect_db
from services import generate_receipt_txt_for_id, view_bookings, get_booking_by_id, compute_balance_status

def update_payment():
    print("\nUpdate Payment")
    view_bookings()

    booking_id = input("\nEnter booking ID to update payment: ").strip()
    if not booking_id.isdigit():
        print("❌ Invalid booking ID.\n")
        return

    booking = get_booking_by_id(int(booking_id))
    if not booking:
        print("❌ Booking not found.\n")
        return

    (bid, name, phone, start, end, btype, event_name,
     rooms, total, paid, method) = booking

    balance = total - paid
    print(f"\nSelected Booking: {bid} - {name} ({btype})")
    print(f"Total: RM {float(total):.2f}")
    print(f"Current paid: RM {float(paid):.2f}")
    print(f"Current balance: RM{float(balance):.2f}")

    top_up = input("Enter additional payment amount (RM): ").strip()
    try:
        top_up = float(top_up)
    except ValueError:
        print("❌ Invalid amount.\n")
        return

    if top_up <= 0:
        print("❌ Payment must be more than 0.\n")
        return

    new_paid = float(paid) + top_up
    if new_paid > float(total):
        new_paid = float(total)  # cap to total

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE bookings
        SET amount_paid = ?
        WHERE id = ?
    """, (new_paid, bid))
    conn.commit()
    conn.close()

    balance, status = compute_balance_status(float(total), new_paid)

    print("\n✅ Payment updated!")
    print(f"New paid: RM {new_paid:.2f}")
    print(f"Balance: RM {balance:.2f}")
    print(f"Status: {status}\n")

    choice = input("Generate updated receipt now? (y/n): ").strip().lower()
    if choice == "y":
        filename = generate_receipt_txt_for_id(bid)
        if filename:
            print(f"✅ Updated receipt generated: {filename}\n")
