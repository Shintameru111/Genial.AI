
from datetime import datetime, timedelta


# ==========================================
# GENIAL.AI - SALON BOOKING SYSTEM
# ==========================================


# 1. SALON INFORMATION

salon_name = "Glow Beauty Salon"


# 2. SERVICE CATALOG (PRICE IN RUPIAH)

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


# 4. SALON OPERATING HOURS

OPENING_HOUR = 9
CLOSING_HOUR = 21

MAX_DAILY_MINUTES = (
    CLOSING_HOUR - OPENING_HOUR
) * 60

# Temporary booking storage
# Data will disappear when the program is closed.

bookings = []


# 5. DISPLAY AVAILABLE SERVICES

def display_services(service_catalog):

    print(f"\nWelcome to {salon_name}")
    print("\n========== AVAILABLE SERVICES ==========")

    for number, (service, price) in enumerate(
        service_catalog.items(), start=1
    ):

        formatted_price = f"{price:,}".replace(",", ".")

        print(
            f"{number}. {service}: Rp {formatted_price}"
        )


# 6. SELECT MULTIPLE SERVICES

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


# 7. CHECK BOOKING AVAILABILITY


def check_availability(new_start, duration_minutes):

    new_end = new_start + timedelta(
        minutes=duration_minutes
    )

    # Get salon opening and closing times

    opening_time = new_start.replace(
        hour=OPENING_HOUR,
        minute=0,
        second=0,
        microsecond=0
    )

    closing_time = new_start.replace(
        hour=CLOSING_HOUR,
        minute=0,
        second=0,
        microsecond=0
    )

    # Check whether booking starts before opening

    if new_start < opening_time:
        return False, "Our salon opens at 09:00."

    # Check whether booking ends after closing

    if new_end > closing_time:
        return False, "Our salon closes at 21:00."

    # Check existing bookings

    for booking in bookings:

        existing_start = booking["start"]
        existing_end = booking["end"]

        if (
            new_start < existing_end
            and existing_start < new_end
        ):
            return False, "This time slot is already booked."

    return True, "This time slot is available."


# 8. FIND THE NEXT AVAILABLE SLOT

def find_next_available_slot(
    requested_start,
    duration_minutes,
    max_days=30
):

    candidate = requested_start

    last_date = (
        requested_start.date()
        + timedelta(days=max_days)
    )

    while candidate.date() <= last_date:

        opening_time = candidate.replace(
            hour=OPENING_HOUR,
            minute=0,
            second=0,
            microsecond=0
        )

        closing_time = candidate.replace(
            hour=CLOSING_HOUR,
            minute=0,
            second=0,
            microsecond=0
        )

        # Move to opening time if necessary

        if candidate < opening_time:

            candidate = opening_time

        # Move to the next day if the service
        # cannot finish before closing time

        if (
            candidate + timedelta(minutes=duration_minutes)
            > closing_time
        ):

            candidate = (
                candidate + timedelta(days=1)
            ).replace(
                hour=OPENING_HOUR,
                minute=0,
                second=0,
                microsecond=0
            )

            continue

        # Check whether the candidate slot is available

        available, message = check_availability(
            candidate,
            duration_minutes
        )

        if available:

            return candidate

        # Try another slot after 15 minutes

        candidate += timedelta(minutes=15)

    return None


# 9. BOOK APPOINTMENT

def book_appointment(service_catalog, duration_catalog):

    print("\n========== BOOK YOUR APPOINTMENT ==========")

    customer_name = input(
        "Enter your name: "
    ).strip()

    if not customer_name:

        print("Customer name cannot be empty.")
        return

    selected_services = select_service(service_catalog)

    if selected_services is None:

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

    # Check maximum daily duration

    if total_duration > MAX_DAILY_MINUTES:

        print("\n========== ADMIN ASSISTANCE ==========")

        print(
            "This booking requires special scheduling."
        )

        print(
            "The total service duration exceeds "
            "the salon's 12-hour operating window."
        )

        print(
            "Please contact our salon administrator."
        )

        return

    # Ask for appointment date and time

    appointment_date = input(
        "\nEnter appointment date (DD-MM-YYYY): "
    ).strip()

    appointment_time = input(
        "Enter appointment time (HH:MM): "
    ).strip()

    # Validate date and time

    try:

        requested_start = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%d-%m-%Y %H:%M"
        )

    except ValueError:

        print("\nInvalid date or time format.")
        print("Use DD-MM-YYYY and HH:MM.")

        return

    # Prevent past bookings

    if requested_start <= datetime.now():

        print("\nYou cannot book a time in the past.")
        return

    # Check requested availability

    available, message = check_availability(
        requested_start,
        total_duration
    )

    final_start = requested_start

    # Search for an alternative if unavailable

    if not available:

        print("\nRequested time is unavailable.")
        print(message)

        print("\nSearching for the next available slot...")

        suggested_start = find_next_available_slot(
            requested_start,
            total_duration
        )

        if suggested_start is None:

            print("\nNo available slot found within 30 days.")

            print(
                "Please contact our salon administrator."
            )

            return

        print("\n========== ALTERNATIVE SLOT ==========")

        print(
            "Suggested Date:",
            suggested_start.strftime("%d-%m-%Y")
        )

        print(
            "Suggested Time:",
            suggested_start.strftime("%H:%M")
        )

        choice = input(
            "\nWould you like this suggested slot? (yes/no): "
        ).strip().lower()

        if choice != "yes":

            print("\nBooking cancelled.")
            return

        final_start = suggested_start

    # Calculate final end time

    final_end = final_start + timedelta(
        minutes=total_duration
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

    formatted_total = f"{total_price:,}".replace(",", ".")

    hours = total_duration // 60
    minutes = total_duration % 60

    print(f"\nTotal Price: Rp {formatted_total}")

    print(
        f"Estimated Duration: "
        f"{hours} hours {minutes} minutes"
    )

    print(
        "Start:",
        final_start.strftime("%d-%m-%Y %H:%M")
    )

    print(
        "End:",
        final_end.strftime("%d-%m-%Y %H:%M")
    )

    # Confirm booking

    confirmation = input(
        "\nConfirm your booking? (yes/no): "
    ).strip().lower()

    if confirmation == "yes":

        # Save booking in temporary storage

        bookings.append({
            "customer": customer_name,
            "services": selected_services,
            "start": final_start,
            "end": final_end,
            "total_price": total_price
        })

        print("\nYour booking has been confirmed!")

        print(
            f"Thank you for choosing {salon_name}."
        )

    else:

        print("\nBooking cancelled.")


# 10. RUN THE PROGRAM

if __name__ == "__main__":

    book_appointment(services, service_durations)
