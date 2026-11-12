# Genial.AI - Salon Service Catalog

salon_name = "Glow Beauty Salon"

services = {
    "Haircut": 50000,
    "Haircut & Styling": 100000,
    "Hair Coloring": 150000,
    "Hair Highlights": 200000,
    "Hair Wash": 30000,
    "Hair Treatment": 100000,
    "Manicure and Pedicure": 175000,
    "Facial Treatment": 200000,
    "Makeup Application": 250000,
    "Bridal Makeup": 500000,
    "Eyebrow Threading": 40000,
    "Eyelash Extensions": 300000,
    "Waxing": 80000,
    "Skincare Consultation": 150000,
    "Massage Therapy": 200000,
    "bridal package": 1500000,
    "spa package": 1000000,
    "hair spa": 250000,
    "nail art": 100000,
    "bridal hair styling": 300000,
    "bridal makeup trial": 200000,
    "bridal hair trial": 150000,
    "bridal package with makeup and hair": 2000000
}


def display_services(service_catalog):
    print(f"\nWelcome to {salon_name}")
    print("\nAvailable Services:")

    for number, (service, price) in enumerate(service_catalog.items(), start=1):
        formatted_price = f"{price:,}".replace(",", ".")
        print(f"{number}. {service}: Rp {formatted_price}")


def select_service(service_catalog):
    display_services(service_catalog)

    service_list = list(service_catalog.items())

    print("\nYou can select multiple services.")
    print("Example: 1, 2, 4")

    selected_input = input(
        "\nEnter service numbers: "
    ).strip()

    try:
        selected_numbers = [
            int(number.strip())
            for number in selected_input.split(",")
        ]
    except ValueError:
        print("Please enter valid numbers.")
        return None

    if not selected_numbers:
        print("Please select at least one service.")
        return None

    if len(set(selected_numbers)) != len(selected_numbers):
        print("Duplicate selections are not allowed.")
        return None

    if any(number < 1 or number > len(service_list)
           for number in selected_numbers):
        print("One or more service numbers are invalid.")
        return None

    selected_services = [
        service_list[number - 1]
        for number in selected_numbers
    ]

    return selected_services



def book_appointment(service_catalog):

    print("\n===== BOOK YOUR APPOINTMENT =====")

    customer_name = input("Enter your name: ").strip()

    if not customer_name:
        print("Customer name cannot be empty.")
        return

    selected_services = select_service(service_catalog)

    if selected_services is None:
        return

    appointment_date = input(
        "\nEnter appointment date (DD-MM-YYYY): "
    ).strip()

    appointment_time = input(
        "Enter appointment time (HH:MM): "
    ).strip()

    total_price = sum(
        price for service, price in selected_services
    )

    print("\n===== BOOKING SUMMARY =====")
    print(f"Customer: {customer_name}")

    print("\nSelected Services:")

    for service, price in selected_services:
        formatted_price = f"{price:,}".replace(",", ".")
        print(f"- {service}: Rp {formatted_price}")

    formatted_total = f"{total_price:,}".replace(",", ".")

    print(f"\nTotal Price: Rp {formatted_total}")
    print(f"Date: {appointment_date}")
    print(f"Time: {appointment_time}")

    confirmation = input(
        "\nConfirm your booking? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":
        print("\nYour booking request has been confirmed!")
    else:
        print("\nBooking cancelled.")
book_appointment(services)
