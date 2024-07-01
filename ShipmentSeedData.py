import csv
from faker import Faker
import random
from datetime import datetime, timedelta
import os

NUMBER_OF_SHIPMENTS = 50

fake = Faker()


# "Shipment" ClientIDs should only be generated from "Client" ClientIDs in "clients.csv" file
def get_client_ids(filename="clients.csv"):
    client_ids = []
    with open(filename, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            client_ids.append(row['ClientID'])
    f.close()
    return client_ids


# Select Tracking URL based on randomized Carrier
def select_tracking_url(carrier):
    tracking_urls = {
        "FedEx": "https://www.fedex.com/en-us/tracking.html",
        "UPS": "https://www.ups.com/track?loc=en_US",
        "USPS": "https://tools.usps.com/go/TrackConfirmAction_input",
        "DHL": "https://www.dhl.com/us-en/home/tracking.html",
        "Amazon": "https://track.amazon.com/"
    }
    tracking_url = tracking_urls.get(carrier, "No tracking URL available")
    return tracking_url


# Generate shipment data
def generate_shipment_data(client_ids):

    shipment_id = fake.uuid4()
    client_id = random.choice(client_ids)
    company_id = fake.uuid4()
    company_name = fake.company()
    shipment_date = fake.date_between(start_date='-1y', end_date='today')
    expected_delivery_date = shipment_date + timedelta(days=random.randint(1, 10))
    actual_delivery_date = expected_delivery_date + timedelta(days=random.randint(-2, 5))
    origin_address = fake.address().replace("\n", ", ")
    destination_address = fake.address().replace("\n", ", ")
    statuses = ['on time', 'delayed', 'lost in transit']
    status = random.choice(statuses)
    tracking_number = fake.uuid4()
    carriers = ['FedEx', 'UPS', 'USPS', 'DHL', 'Amazon']
    carrier = random.choice(carriers)
    tracking_url = select_tracking_url(carrier)
    shipment_types = ['standard', 'express', 'overnight']
    shipment_type = random.choice(shipment_types)
    weight = round(random.uniform(1, 100), 2)  # Weight in kilograms
    dimensions = f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}"  # Dimensions in cm
    contents_description_list = [
        "Books and stationery supplies",
        "Electronic gadgets and accessories",
        "Clothing and fashion accessories",
        "Furniture and home decor items",
        "Toys and children's play equipment",
        "Medical supplies and pharmaceuticals",
        "Food items and beverages",
        "Office supplies and stationery",
        "Sports equipment and gear",
        "Machinery parts and industrial tools",
        "Gardening tools and outdoor equipment",
        "Beauty products and cosmetics",
        "Household items and appliances",
        "Automotive parts and accessories",
        "Cleaning supplies and hygiene products"
    ]
    contents_description = random.choice(contents_description_list)
    special_instructions_list = [
        "Handle with care. Fragile items inside. Keep upright and avoid direct sunlight.",
        "Keep refrigerated. Temperature-sensitive materials inside. Do not freeze.",
        "Fragile. Glass items enclosed. Do not stack and avoid heavy pressure.",
        "Handle with care. High-value electronics. Keep dry and avoid moisture.",
        "This side up. Perishable goods inside. Do not tilt or drop. Store in cool place.",
        "Sensitive equipment. Do not bend or crush. Store upright. Keep away from magnets.",
        "Handle gently. Artwork enclosed. Avoid direct contact. Deliver for inspection.",
        "Do not open. Confidential documents inside. Deliver directly. Maintain confidentiality.",
        "Perishable goods. Keep refrigerated at 4°C. Handle with gloves. Deliver before lunch.",
        "Heavy items. Use lifting equipment. Do not attempt manual handling. Deliver to dock.",
        "Flammable materials. Store ventilated area. Handle with protective gear. Deliver safely.",
        "Handle with gloves. Biological samples inside. Keep frozen at -20°C. Deliver directly.",
        "Delicate instruments. Calibration required. Handle with care. Deliver for inspection.",
        "Keep dry. Water-sensitive equipment inside. Protect from humidity. Deliver carefully.",
        "Handle with care. Antiques enclosed. Use padding. Deliver to customer's home."
    ]
    special_instructions = random.choice(special_instructions_list)
    insurance_amount = round(random.uniform(100.0, 10000.0), 2)  # Insurance amount in currency
    shipping_cost = round(random.uniform(10.0, 500.0), 2)  # Shipping cost in currency
    payment_statuses = ['paid', 'unpaid', 'pending']
    payment_status = random.choice(payment_statuses)
    notes = ''  # Empty Notes field
    shipment_data = (
        [
            shipment_id, client_id, company_id, company_name, shipment_date, expected_delivery_date,
            actual_delivery_date, origin_address, destination_address, status, tracking_number,
            tracking_url, carrier, shipment_type, weight, dimensions, contents_description,
            special_instructions, insurance_amount, shipping_cost, payment_status, notes
        ]
    )

    return shipment_data


# Main script
def main():
    client_ids = get_client_ids()
    shipments = []
    for _ in range(NUMBER_OF_SHIPMENTS):
        shipment = generate_shipment_data(client_ids)
        shipments.append(shipment)

    # Define CSV headers
    headers = [
        'ShipmentID', 'ClientID', 'CompanyID', 'CompanyName', 'ShipmentDate', 'ExpectedDeliveryDate',
        'ActualDeliveryDate', 'OriginAddress', 'DestinationAddress', 'Status', 'TrackingNumber',
        'TrackingURL', 'Carrier', 'ShipmentType', 'Weight', 'Dimensions', 'ContentsDescription',
        'SpecialInstructions', 'InsuranceAmount', 'ShippingCost', 'PaymentStatus', 'Notes'
    ]

    # Write to CSV
    with open('shipments.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(shipments)

    print("CSV file 'shipments.csv' with 50 rows of fake shipment data has been created.")


if __name__ == "__main__":
    main()
