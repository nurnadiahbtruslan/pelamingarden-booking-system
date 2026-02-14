# app_cli.py
from db import create_table

from bookings import (
    add_booking,
    view_bookings,
    search_by_date,
    delete_booking,
    check_availability
)

from payments import update_payment
from receipts import generate_receipt_txt
from reports import show_summary, monthly_report, export_to_csv


def main():
    create_table()
    
    while True:
        print("\nBooking System")
        print("1. Add new booking")
        print("2. View all bookings")
        print("3. Search bookings by date")
        print("4. Delete booking")
        print("5. View business summary")
        print("6. Monthly revenue report")
        print("7. Export bookings to CSV")
        print("8. Check availability")
        print("9. Generate receipt")
        print("10. Update payment")
        print("11. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_booking()
        elif choice == "2":
            view_bookings()
        elif choice == "3":
            search_by_date()
        elif choice == "4":
            delete_booking()
        elif choice == "5":
            show_summary()
        elif choice == "6":
            monthly_report()
        elif choice == "7":
            export_to_csv()
        elif choice == "8":
            check_availability()
        elif choice == "9":
            generate_receipt_txt()
        elif choice == "10":
            update_payment()
        elif choice == "11":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Try again.\n")


if __name__ == "__main__":
    main()