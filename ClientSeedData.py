import csv
from faker import Faker
import random
from datetime import datetime, timedelta

NUMBER_OF_CLIENTS = 50

fake = Faker()


# Generates N Clients
def generate_client_data():

    client_id = fake.uuid4()
    client_name = fake.name()
    client_email = fake.email()
    client_phone_number = fake.phone_number()
    client_address = fake.address().replace("\n", ", ")
    job_title = fake.job()
    employer_id = fake.uuid4()
    employer_name = fake.company()
    client_billing_information = fake.credit_card_full()
    client_order_history = [fake.uuid4() for _ in range(random.randint(1, 10))]
    date_of_registration = fake.date_between(start_date='-5y', end_date='today')
    date_last_contacted = date_of_registration + timedelta(days=random.randint(0, 1800))
    preferred_contact_time = f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
    notes = ''  # Empty Notes field

    client_data = [
            client_id, client_name, client_email, client_phone_number, client_address,
            job_title, employer_id, employer_name, client_billing_information,
            client_order_history, date_of_registration, date_last_contacted,
            preferred_contact_time, notes
        ]

    return client_data


# Main function
def main():
    # Generate client data
    clients = []
    for _ in range(NUMBER_OF_CLIENTS):
        client = generate_client_data()
        clients.append(client)

    # Define CSV headers
    headers = [
        'ClientID', 'ClientName', 'ClientEmail', 'ClientPhoneNumber', 'ClientAddress',
        'JobTitle', 'EmployerID', 'EmployerName', 'ClientBillingInformation',
        'ClientOrderHistory', 'DateOfRegistration', 'DateLastContacted',
        'PreferredContactTime', 'Notes'
    ]

    # Write to CSV
    with open('clients.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(clients)

    print("CSV file 'clients.csv' with 50 rows of fake client data has been created.")


if __name__ == "__main__":
    main()
