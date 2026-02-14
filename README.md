🚀 Pelamin Garden Booking System (CLI Version)

📌 Project Overview

A modular Python CLI-based booking management system built for a real-world homestay and event venue business.

This system automates:
	•	Booking management
	•	Event blocking rules
	•	Homestay room capacity validation
	•	Receipt generation
	•	Payment tracking & updates
	•	Monthly revenue reporting
	•	CSV export

Built with Python and SQLite following clean modular architecture.

_____________________________________________________________________________________________

🎯 Real Business Problems Solved

Previously, bookings were:
	•	Tracked manually via WhatsApp
	•	Managed via Word receipts
	•	Monitored via bank history
	•	No clear monthly profit overview

This system provides:
	•	Centralised booking database
	•	Conflict detection (event blocks homestay)
	•	Automated receipt generation
	•	Real-time payment balance tracking
	•	Business summary & monthly revenue report

_____________________________________________________________________________________________

🧠 Key Features

🏠 Booking Logic
	•	Supports homestay and event types
	•	Event bookings block entire date range
	•	Homestay bookings enforce 5-room capacity rule
	•	Date overlap validation

💰 Payment Management
	•	Track total amount & amount paid
	•	Auto-calculate balance
	•	Payment status: Unpaid / Partial / Paid
	•	Payment update flow

🧾 Receipt Generation
	•	Auto-generate TXT receipt on booking creation
	•	Option to regenerate after payment update
	•	Dynamic receipt number format:
        PG-YYYYMMDD-XXXX

📊 Reporting
	•	Total customer count
	•	Total revenue
	•	Monthly revenue aggregation
	•	CSV export

_____________________________________________________________________________________________

🛠 Tech Stack
	•	Python 3
	•	SQLite
	•	CLI-based interaction
	•	Modular architecture
	•	Git version control

_____________________________________________________________________________________________

🧩 Project Structure
venue-system/
│
├── app_cli.py
├── db.py
├── bookings.py
├── payments.py
├── receipts.py
├── reports.py
├── services.py
├── bookings.db (ignored)
├── receipts/ (ignored)
└── README.md

_____________________________________________________________________________________________

🧱 Architecture
	•	db.py → Database connection logic
	•	bookings.py → Booking rules & validation
	•	payments.py → Payment updates
	•	receipts.py → Receipt generation
	•	services.py → Shared logic
	•	reports.py → Business reporting
	•	app_cli.py → User interface

Follows separation of concerns principle.

_____________________________________________________________________________________________

▶️ How To Run
python app_cli.py

_____________________________________________________________________________________________

📈 Future Improvements
	•	Flask REST API version
	•	Web UI dashboard
	•	Authentication & user roles
	•	Cloud deployment
	•	Automated testing (unit tests)
	•	Payment integration

_____________________________________________________________________________________________

👩‍💻 About Me

This project was built as part of my journey to strengthen backend engineering, system design, and real-world business automation skills.