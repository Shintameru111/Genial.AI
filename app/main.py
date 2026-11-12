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

    for service, price in service_catalog.items():
        formatted_price = f"{price:,}".replace(",", ".")
        print(f"- {service}: Rp {formatted_price}")


display_services(services)