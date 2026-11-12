
# ==========================================
# GENIAL.AI - SALON BOOKING SYSTEM
# ==========================================


# 1. SALON INFORMATION

salon_name = "Glow Beauty Salon"


# 2. SERVICE CATALOG (SERVICE NAME AND PRICE)

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


# 3. SERVICE DURATION (IN MINUTES)

service_durations = {
    "Haircut": 30,
    "Haircut & Styling": 60,
    "Hair Coloring": 120,
    "Hair Highlights": 180,
    "Hair Wash": 20,
    "Hair Treatment": 60,
    "Manicure and Pedicure": 90,
    "Facial Treatment": 60,
    "Makeup Application": 60,
    "Bridal Makeup": 120,
    "Eyebrow Threading": 15,
    "Eyelash Extensions": 120,
    "Waxing": 30,
    "Skincare Consultation": 30,
    "Massage Therapy": 60,
    "bridal package": 240,
    "spa package": 120,
    "hair spa": 90,
    "nail art": 60,
    "bridal hair styling": 90,
    "bridal makeup trial": 90,
    "bridal hair trial": 90,
    "bridal package with makeup and hair": 300
}


# 4. DISPLAY AVAILABLE SERVICES

def display_services(service_catalog):

    print(f"\nWelcome to {salon_name}")
    print("\n========== AVAILABLE SERVICES ==========")

    for number, (service, price) in enumerate(
        service_catalog.items(), start=1
    ):
        formatted_price = f"{price:,}".replace(",", ".")
        print(f"{number}. {service}: Rp {formatted_price}")


# 5. SELECT MULTIPLE SERVICES

def select_service(service_catalog):

    display_services(service_catalog)

    service_list = list(service_catalog.items())

    print("\nYou can select multiple services.")
    print("Example: 1, 2, 4")

    selected_input = input(
        "\nEnter service numbers: "
    ).strip()

    if not selected_input:
        print("Please select at least one service.")
        return None

    try:
        selected_numbers = [
            int(number.strip())
            for number in selected_input.split(",")
        ]

    except ValueError:
        print("Invalid input. Please enter numbers only.")
        return None

    if len(set(selected_numbers)) != len(selected_numbers):
        print("Duplicate selections are not allowed.")
        return None

    if any(
        number < 1 or number > len(service_list)
        for number in selected_numbers
    ):
        print("One or more service numbers are invalid.")
        return None

    selected_services = [
        service_list[number - 1]
        for number in selected_numbers
    ]

    return selected_services


# 6. BOOK APPOINTMENT

def book_appointment(service_catalog, duration_catalog):

    print("\n========== BOOK YOUR APPOINTMENT ==========")

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

    if not appointment_date or not appointment_time:
        print("Date and time cannot be empty.")
        return

    # Calculate total price

    total_price = sum(
        price for service, price in selected_services
    )

    # Calculate total duration

    total_duration = sum(
        duration_catalog[service]
        for service, price in selected_services
    )

    # Display booking summary

    print("\n========== BOOKING SUMMARY ==========")

    print(f"Customer: {customer_name}")

    print("\nSelected Services:")

    for service, price in selected_services:

        formatted_price = f"{price:,}".replace(",", ".")
        duration = duration_catalog[service]

        print(
            f"- {service}: Rp {formatted_price} "
            f"({duration} minutes)"
        )

    # Format total price

    formatted_total = f"{total_price:,}".replace(",", ".")

    # Convert minutes into hours and minutes

    hours = total_duration // 60
    minutes = total_duration % 60

    print(f"\nTotal Price: Rp {formatted_total}")
    print(
        f"Estimated Duration: "
        f"{hours} hours {minutes} minutes"
    )

    print(f"Date: {appointment_date}")
    print(f"Time: {appointment_time}")

    # Booking confirmation

    confirmation = input(
        "\nConfirm your booking? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        print("\nYour booking request has been confirmed!")
        print(f"Thank you for choosing {salon_name}.")

    else:

        print("\nYour booking has been cancelled.")


# 7. RUN THE PROGRAM

if __name__ == "__main__":
    book_appointment(services, service_durations)
