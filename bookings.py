# bookings.py
from db import connect_db, fetch_one, execute, fetch_all_bookings, fetch_total_revenue, insert_booking, get_overlapping_bookings, update_payment_db, get_booking_by_id, delete_booking_db
from services import generate_receipt_txt_for_id, view_bookings, calc_payment_status, generate_receipt_pdf

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


def get_all_bookings():
    rows = fetch_all_bookings()

    bookings = []

    for row in rows:
        booking_id, name, phone, start, end, event_type, event_name, rooms, total, paid = row

        total = total or 0
        paid = paid or 0
        status = calc_payment_status(total, paid)

        bookings.append({
            "id": booking_id,
            "name": name,
            "phone": phone,
            "start": start,
            "end": end,
            "type": event_type,
            "ename": event_name,
            "rooms": rooms,
            "total": total,
            "paid": paid,
            "balance": total - paid,
            "status": status
        })

    bookings.sort(key=lambda b: b["start"])

    return bookings

def get_booking_by_id_service(booking_id):
    booking = get_booking_by_id(booking_id)
    if not booking:
        return {"error": "Booking not found"}, 404
    
    paid = booking["amount_paid"]
    total = booking["total_amount"]
    balance = total - paid
    status = calc_payment_status(total, paid)

    booking["balance"] = balance
    booking["status"] = status
    
    return booking, 200

def get_business_summary():
    total_revenue = fetch_total_revenue()
    return {
        "total_revenue": total_revenue
    }

MAX_ROOMS = 5

def check_availability(data):
    existing = get_overlapping_bookings(
        data["start_date"],
        data["end_date"]
    )

    new_type = data["event_type"]
    rooms = data["rooms"]

    #rule 1: event cannot overlap anything
    if new_type == "event" and existing:
        return False, "Event booking cannot overlap", 0
    
    #rule 2: existing event blocks everything
    for e in existing:
        if e[0] == "event":
            return False, "Date blocked by event", 0

    #rule 3: homestay capacity
    if new_type == "homestay":
        total_booked = 0

        for e in existing:
            if e[0] == "homestay":
                total_booked += e[1]

        rooms_available = MAX_ROOMS - total_booked

        if rooms_available <= 0:
            return False, f"{rooms_available} rooms available", 0
        
        if rooms > MAX_ROOMS:
            return False, f"Rooms cannot exceed {MAX_ROOMS}", 0
        
        if rooms > rooms_available:
            return False, f"{rooms_available} rooms available", 0

        return True, f"{rooms_available} Rooms available", rooms_available

    return True, "Available", 0 

def check_availability_service(data):
    available, message, rooms_available = check_availability(data)

    return{
        "available": available,
        "message": message,
        "rooms_available": rooms_available
    }, 200

def create_booking_service(data):

    data["event_type"] = data["event_type"].strip().lower()

    required_fields = [
        "customer_name",
        "event_type",
        "start_date",
        "end_date",
        "total_amount",
        "amount_paid"
    ]

    for field in required_fields:
        if field not in data:
            return {"error": f"{field} is required"}, 400

    if data["event_type"] not in ["event", "homestay"]:
        return {"error": "Invalid event type"}, 400
    
    if data["start_date"] > data["end_date"]:
        return {"error": "Invalid date range"}, 400

    available, message, _ = check_availability(data)
    if not available:
        return {"error": message}, 409

    paid = float(data.get("amount_paid", 0))
    total = float(data.get("total_amount",0))
    
    data["status"] = calc_payment_status(total, paid)
    data["balance"] = total - paid

    insert_booking(data)

    return {
        "message": "Booking created successfully",
        "balance": data["balance"],
        "status": data["status"]
    }, 201

def update_payment_service(booking_id, amount):
    
    booking = get_booking_by_id(booking_id)

    if not booking:
        return {"error": "Booking not found"}, 404
    
    current_paid = booking["amount_paid"]
    total = booking["total_amount"]
    new_payment = amount

    if new_payment <=0:
        return {"error": "Invalid payment amount"}, 400

    updated_paid = current_paid + new_payment
    balance = total - updated_paid

    status = calc_payment_status(total, updated_paid)

    update_payment_db(booking_id, updated_paid)

    return {
        "message": "Payment updated successfully",
        "amount_paid": updated_paid,
        "balance": balance,
        "status": status
    }, 200


def delete_booking_service(booking_id):
    
    booking = get_booking_by_id(booking_id)

    if not booking:
        return {"error": "Booking not found"}, 404
    
    delete_booking_db(booking_id)

    return {"message": f"Successfully deleted booking id {booking_id}"}, 200


def generate_receipt_sevice(booking_id):

    booking = get_booking_by_id(booking_id)

    if not booking:
        return {"error": "Booking not found"}, 404
    
    paid = booking["amount_paid"]
    total = booking["total_amount"]
    balance = total - paid
    status = calc_payment_status(total, paid)

    booking["balance"] = balance
    booking["status"] = status

    file_name = generate_receipt_pdf(booking)

    return file_name, 200


#for testing only
if __name__ == "__main__":
    # result = get_all_bookings()
    # print(result)
    print(type((1)))
    print(type((1,)))
