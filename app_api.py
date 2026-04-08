from flask import Blueprint, jsonify, request, send_file
from bookings import get_all_bookings, get_business_summary, create_booking_service, update_payment_service, delete_booking_service, generate_receipt_sevice, check_availability_service, get_booking_by_id_service

booking_bp = Blueprint("bookings", __name__)

@booking_bp.route("/bookings", methods=["GET"])
def list_bookings():
    bookings = get_all_bookings()
    return jsonify(bookings), 200

@booking_bp.route("/bookings/<int:booking_id>", methods=["GET"])
def get_booking_api(booking_id):
    result, status = get_booking_by_id_service(booking_id)
    return jsonify(result), status

@booking_bp.route("/summary", methods=["GET"])
def summary():
    result = get_business_summary()
    return jsonify(result), 200

@booking_bp.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()
    result, status = create_booking_service(data)
    return jsonify(result), status

@booking_bp.route("/bookings/<int:booking_id>/payment", methods=["PUT"])
def update_payment(booking_id):
    data = request.get_json()
    amount = float(data.get("amount_paid", 0))
    result, status = update_payment_service(booking_id, amount)
    return jsonify(result), status

@booking_bp.route("/bookings/<int:booking_id>", methods=["DELETE"])
def delete_booking(booking_id):
    result, status = delete_booking_service(booking_id)
    return jsonify(result), status

@booking_bp.route("/bookings/<int:booking_id>/receipt", methods=["GET"])
def generate_receipt_api(booking_id):
    file_name, status = generate_receipt_sevice(booking_id)
    
    if status != 200:
        return jsonify(file_name), status

    return send_file(file_name, as_attachment=True)

@booking_bp.route("/availability", methods=["GET"])
def check_availability_api():
    data = {
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "event_type": request.args.get("event_type"),
        "rooms": int(request.args.get("rooms", 0))
    }

    result, status = check_availability_service(data)

    return jsonify(result), status