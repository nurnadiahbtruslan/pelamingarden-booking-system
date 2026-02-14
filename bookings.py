# bookings.py
from db import connect_db, fetch_one, execute
from services import generate_receipt_txt_for_id, view_bookings, calc_payment_status

# bookings.py
from db import fetch_one

MAX_ROOMS = 5

def has_event_conflict(req_start, req_end):
    return fetch_one("""
        SELECT id, customer_name, start_date, end_date
        FROM bookings
        WHERE lower(event_type) = 'event'
          AND start_date <= ? AND end_date >= ?
    """, (req_end, req_start))

def used_homestay_rooms(req_start, req_end):
    row = fetch_one("""
        SELECT COALESCE(SUM(rooms), 0)
        FROM bookings
        WHERE lower(event_type) = 'homestay'
          AND start_date <= ? AND end_date >= ?
    """, (req_end, req_start))
    return int(row[0]) if row else 0

def any_booking_conflict(req_start, req_end):
    return fetch_one("""
        SELECT id, customer_name, start_date, end_date, event_type
        FROM bookings
        WHERE start_date <= ? AND end_date >= ?
        LIMIT 1
    """, (req_end, req_start))

def validate_booking(start_date, end_date, event_type, rooms_needed=0):
    event_type = (event_type or "").strip().lower()

    if event_type not in ("event", "homestay"):
        return False, "❌ Invalid booking type. Use 'event' or 'homestay'."

    # Rule 1: If an EVENT exists in range, nothing else can be booked
    event = has_event_conflict(start_date, end_date)
    if event:
        return False, f"❌ NOT AVAILABLE: Event blocks these dates (Booking ID {event[0]})."

    # Rule 2: If booking an EVENT, it cannot overlap ANY booking at all
    if event_type == "event":
        conflict = any_booking_conflict(start_date, end_date)
        if conflict:
            return False, f"❌ Cannot add event: conflicts with Booking ID {conflict[0]} ({conflict[4]})."
        return True, "✅ AVAILABLE for event booking."

    # Rule 3: Homestay uses room capacity
    if event_type == "homestay":
        if rooms_needed <= 0 or rooms_needed > MAX_ROOMS:
            return False, f"❌ Rooms must be between 1 and {MAX_ROOMS}."

        used = used_homestay_rooms(start_date, end_date)
        available = MAX_ROOMS - used

        if rooms_needed > available:
            return False, f"❌ NOT AVAILABLE: only {available} rooms left."
        return True, f"✅ AVAILABLE: {available - rooms_needed} rooms left after booking."

    return False, "❌ Invalid booking type."

# def has_event_conflict(req_start, req_end):
#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT id, customer_name, start_date, end_date
#         FROM bookings
#         WHERE lower(event_type) = 'event'
#           AND start_date <= ? AND end_date >= ?
#     """, (req_end, req_start))
#     row = cur.fetchone()
#     conn.close()
#     return row  # None if no conflict

# def used_homestay_rooms(req_start, req_end):
#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute("""
#         SELECT COALESCE(SUM(rooms), 0)
#         FROM bookings
#         WHERE lower(event_type) = 'homestay'
#           AND start_date <= ? AND end_date >= ?
#     """, (req_end, req_start))
#     total = cur.fetchone()[0]
#     conn.close()
#     return total

# def validate_booking(start_date, end_date, event_type, rooms_needed=0):
#     # Rule 1: If an event already exists, block everything
#     event = has_event_conflict(start_date, end_date)
#     if event:
#         return False, f"❌ Event already blocks these dates (Booking ID {event[0]})."

#     # Rule 2: If booking an event, it cannot overlap ANY booking
#     if event_type == "event":
#         conn = connect_db()
#         cur = conn.cursor()
#         cur.execute("""
#             SELECT id FROM bookings
#             WHERE start_date <= ? AND end_date >= ?
#         """, (end_date, start_date))
#         conflict = cur.fetchone()
#         conn.close()

#         if conflict:
#             return False, "❌ Cannot add event: dates already have bookings."
#         return True, "✅ Event booking allowed."

#     # Rule 3: Homestay room capacity
#     if event_type == "homestay":
#         used = used_homestay_rooms(start_date, end_date)
#         if used + rooms_needed > 5:
#             return False, f"❌ Not enough rooms. Used={used}, Requested={rooms_needed}, Max=5."
#         return True, f"✅ Homestay booking allowed. Rooms left: {5 - (used + rooms_needed)}."

#     return False, "❌ Invalid booking type."

def add_booking():
    print("\nAdd New Booking")

    name = input("Customer name: ").strip()
    phone = input("Phone number: ").strip()

    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()

    event_type = input("Booking type (homestay/event): ").strip().lower()

    event_name = None
    rooms = 0

    if event_type == "event":
        event_name = input("Event name (Wedding/Birthday/etc): ").strip()
        rooms = int(input("Rooms to reserve for event stay (0-5): "))
        if rooms < 0 or rooms > 5:
            print("❌ Rooms must be between 0 and 5.")
            return

        ok, msg = validate_booking(start_date, end_date, event_type, rooms)
        if not ok:
            print("\n" + msg + "\n")
            return

    elif event_type == "homestay":
        rooms = int(input("Number of rooms (1-5): "))
        if rooms < 1 or rooms > 5:
            print("❌ Rooms must be between 1 and 5.")
            return

        ok, msg = validate_booking(start_date, end_date, event_type, rooms)
        if not ok:
            print("\n" + msg + "\n")
            return

    else:
        print("❌ Invalid booking type.\n")
        return

    # Payment info
    try:
        total_amount = float(input("Total amount (RM): ").strip())
        amount_paid = float(input("Amount paid (RM): ").strip())
    except ValueError:
        print("❌ Invalid amount.\n")
        return

    payment_method = input("Payment method (Cash/Transfer/Online): ").strip().lower()

    status = calc_payment_status(total_amount, amount_paid)
    balance = total_amount - amount_paid

    new_booking_id = execute("""
        INSERT INTO bookings (
            customer_name, phone, start_date, end_date,
            event_type, event_name, rooms,
            total_amount, amount_paid, payment_method
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, start_date, end_date, event_type, event_name, rooms,
          total_amount, amount_paid, payment_method))

     # Auto-generate receipt
    filename = generate_receipt_txt_for_id(new_booking_id)

    print(f"\n✅ Booking added! Status: {status}, Balance: RM {balance:.2f}")
    if filename:
        print(f"✅ Receipt auto-generated: {filename}\n")


# def add_booking():
#     print("\nAdd New Booking")
#     name = input("Customer name: ")
#     phone = input("Phone number: ")
#     start_date = input("Start date (YYYY-MM-DD): ")
#     end_date = input("End date (YYYY-MM-DD): ")
#     event_type = input("Event type (homestay/event): ").strip().lower()

#     event_name = None
#     rooms = 0

#     if event_type == "event":
#         event_name = input("Event name (Wedding/Birthday/etc): ").strip()
#         rooms = int(input("Number of rooms (1-5): "))
#     elif event_type == "homestay":
#         rooms = int(input("Number of rooms (1-5): "))
#     else:
#         print("Invalid booking type.")
#         return

#     ok, message = validate_booking(start_date, end_date, event_type, rooms)
#     if not ok:
#         print("\n" + message + "\n")
#         return

#     total_amount = float(input("Total amount (RM): "))
#     amount_paid = float(input("Amount paid (RM): "))
#     payment_method = input("Payment method (Cash/Transfer/Online): ")

#     status = calc_payment_status(total_amount, amount_paid)

#     conn = connect_db()
#     cursor = conn.cursor()
#     cursor.execute("""
#     INSERT INTO bookings (customer_name, phone, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid, payment_method)
#     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (name, phone, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid, payment_method))
#     new_booking_id = cursor.lastrowid
#     conn.commit()
#     conn.close()

#     balance = total_amount - amount_paid
#     filename = generate_receipt_txt_for_id(new_booking_id)
#     if filename:
#         print(f"\nBooking added! Status: {status}, Balance: RM {balance}")
#         print(f"✅ Receipt auto-generated: {filename}\n")

def search_by_date():
    date = input("\nEnter date to search (YYYY-MM-DD): ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, customer_name, start_date, end_date, event_type, event_name, rooms, total_amount, amount_paid
    FROM bookings
    WHERE start_date <= ? AND end_date >= ?
    ORDER BY start_date
    """, (date, date))
    rows = cursor.fetchall()

    conn.close()

    if rows:
        print("\nBookings found:")
        for row in rows:
            print(row)
    else:
        print("\nNo bookings found for this date.")

    print()

def delete_booking():
    view_bookings()
    
    booking_id = input("\nEnter booking ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()

    print("Booking deleted successfully!\n")

def check_availability():
    req_start = input("\nRequested start date (YYYY-MM-DD): ")
    req_end = input("Requested end date (YYYY-MM-DD): ")
    req_type = input("Booking type (homestay/event): ").strip().lower()

    rooms_needed = 0
    if req_type == "homestay":
        rooms_needed = int(input("Rooms needed (1-5): "))

    ok, message = validate_booking(req_start, req_end, req_type, rooms_needed)
    print("\n" + message + "\n")