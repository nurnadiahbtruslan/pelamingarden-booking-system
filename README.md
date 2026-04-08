# Booking Management System

A web-based booking management system built to replace manual processes for a small business (pelamin garden homestay).

## 🚀 Features

- Check availability based on business rules
- Create booking (event / homestay)
- Prevent booking conflicts
- Update payment (partial / full)
- Automatically calculate balance and status
- Generate PDF receipt
- Delete booking
- Simple dashboard to manage bookings

## 🧠 Key Concepts

- REST API design
- Layered architecture (API, Service, Repository)
- Business logic handling (booking conflicts, capacity rules)
- Data validation and error handling
- Frontend integration using Flask templates

## ⚙️ Tech Stack

- Python (Flask)
- SQLite
- HTML (Jinja templates)
- ReportLab (PDF generation)

## 📌 Business Logic Highlights

- Event bookings block all other bookings on selected dates
- Homestay bookings are limited by room capacity
- Prevents overbooking using conflict checking
- Payment system supports partial and full payments

## 💡 Purpose

This system was developed to replace manual workflows such as:
- Tracking bookings via WhatsApp
- Creating receipts manually using Word
- Manually tracking payments

It helps streamline operations and reduce human error.

## ▶️ How to Run

1. Clone the repository
2. Install dependencies
3. Run the Flask app:

```bash
python app.py
```
4. Open in browser:

http://127.0.0.1:5000/

## 📈 Future Improvements
	•	Improve UI/UX design
	•	Deploy system online
	•	Add authentication/login system
	

