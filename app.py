from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from bookings import get_all_bookings, create_booking_service, update_payment_service, get_booking_by_id_service, delete_booking_service, check_availability_service
from app_api import booking_bp

app = Flask(__name__)

app.register_blueprint(booking_bp)

app.secret_key = "pelamingarden"

@app.route("/")
def home():
    bookings = get_all_bookings()
    return render_template("index.html", bookings=bookings)

@app.route("/create-booking", methods=["GET", "POST"])
def create_booking_page():
    if request.method == "POST":
        data = {
            "customer_name": request.form.get("customer_name"),
            "phone": request.form.get("phone"),
            "event_type": request.form.get("event_type"),
            "event_name": request.form.get("event_name"),
            "start_date": request.form.get("start_date"),
            "end_date": request.form.get("end_date"),
            "rooms": int(request.form.get("rooms") or 0),
            "total_amount": float(request.form.get("total_amount") or 0),
            "amount_paid": float(request.form.get("amount_paid") or 0)
        }

        result, status = create_booking_service(data)

        if status != 201:
             flash(result["error"], "error")
             return redirect(url_for("create_booking_page"))
        
        flash("Booking created successfully!","success")
        return redirect(url_for("home"))
    
    return render_template("create_booking.html")

@app.route("/bookings/<int:booking_id>/payment", methods=["GET", "POST"])
def update_payment_page(booking_id):
    if request.method == "POST":
        amount = float(request.form.get("amount_paid", 0))

        result, status = update_payment_service(booking_id, amount)

        if status != 200:
            flash(result["error"], "error")
            return redirect(url_for("update_payment_page", booking_id=booking_id))
        
        flash("Payment updated successfully!","success")
        return redirect(url_for("home"))
    
    booking, status = get_booking_by_id_service(booking_id)

    return render_template("update_payment.html", booking=booking)

@app.route("/bookings/<int:booking_id>/delete")
def delete_booking_page(booking_id):
    result, status = delete_booking_service(booking_id)

    if status != 200:
        flash(result["error"], "error")
    else:
        flash("Booking deleted successfully!","success")

    return redirect(url_for("home"))

@app.route("/availability-ui")
def availability_ui():
    data = {
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "event_type": request.args.get("event_type"),
        "rooms": int(request.args.get("rooms") or 0)
    }

    result, status = check_availability_service(data)

    return render_template("availability_result.html", result=result)
# @app.route("/")
# def home():
#     return render_template("home.html")

# @app.route("/bookings")
# def bookings():
#     data = get_all_bookings()
#     return render_template("bookings.html", bookings=data, total_bookings=len(data), total_revenue=total_revenue)

if __name__ == "__main__":
    app.run(debug=True)