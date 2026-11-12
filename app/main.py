# Genial.AI - Salon Service Catalog

salon_name = "Glow Beauty Salon"

services = {
    "Haircut": 50000,
    "Hair Coloring": 150000,
    "Hair Wash": 30000,
    "Hair Treatment": 100000
}


def display_services(service_catalog):
    print(f"\nWelcome to {salon_name}")
    print("\nAvailable Services:")

    for service, price in service_catalog.items():
        formatted_price = f"{price:,}".replace(",", ".")
        print(f"- {service}: Rp {formatted_price}")


display_services(services)