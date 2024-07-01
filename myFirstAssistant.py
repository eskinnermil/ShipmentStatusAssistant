import streamlit as st
import pandas as pd
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from openai import OpenAI
import os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, GridUpdateMode
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_PASSWORD = os.getenv("FROM_PASSWORD")
EMAIL_SERVER_URL = os.getenv("EMAIL_SERVER_URL")
EMAIL_PORT_NUMBER = os.getenv("EMAIL_PORT_NUMBER")
CLIENTS_FILE = os.getenv("CLIENTS_FILE")
SHIPMENT_FILE = os.getenv("SHIPMENTS_FILE")
YOUR_COMPANY_NAME = "SONA AP LOGISTICS"
CARE_LINE_PHONE_NUMBER = "1-888-555-5555"


def get_shipment_status(clients_df, shipments_df, client_id, shipment_id):
    merged_df = pd.merge(clients_df, shipments_df, on='ClientID', how='inner')
    filter_condition = \
        (merged_df['ClientID'] == client_id) & \
        (merged_df['ShipmentID'] == shipment_id)
    filtered_data = merged_df[filter_condition]
    st.write(filtered_data)

    # if not filtered_data.empty:
    try:
        status = filtered_data.iloc[0]['Status']
        expected_delivery_date = filtered_data.iloc[0]['ExpectedDeliveryDate']
        client_name = filtered_data.iloc[0]['ClientName']
        client_email = filtered_data.iloc[0]['ClientEmail']
        tracking_number = filtered_data.iloc[0]['TrackingNumber']
        tracking_url = filtered_data.iloc[0]['TrackingURL']
        carrier = filtered_data.iloc[0]['Carrier']
        return status, expected_delivery_date, client_name, client_email, \
               tracking_number, tracking_url, carrier
    except Exception as e:
        st.error(f"At least one file was empty. Please populate the file(s): {e}")


def send_email(expected_delivery_date, client_name, client_email, prompt, shipment_id, tracking_number,
               tracking_url, carrier):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "You are a helpful assistant generating email content for a logistics company. "
                f"The email should include the following details clearly: {str(tracking_number)}, {tracking_url}, {carrier},"
                f" {expected_delivery_date}."
                "Write the email body in paragraph format without a subject, greeting, or closing."
            )},
            {"role": "user", "content": prompt},
        ],
        max_tokens=200
    )
    generated_text = response.choices[0].message.content.strip()

    # # Don't finish generating text on an incomplete sentence
    # sentences = generated_text.split(". ")
    # if len(sentences) == 1:
    #     complete_text = generated_text
    # complete_text = ". ".join(sentences[:-1])
    # if not complete_text.endswith('.'):
    #     complete_text += '.'

    # Email body
    message = f"""
    Dear {client_name},
    
    {generated_text}
    
    If you have any questions or concerns, feel free to reach out to our Customer Care line at {CARE_LINE_PHONE_NUMBER}.
    
    Best Regards,
    {YOUR_COMPANY_NAME}
    """

    # Setup email
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = FROM_EMAIL
    msg['Subject'] = f"An Update On Your Shipment {shipment_id}"
    msg.attach(MIMEText(message, 'plain'))

    # Send email using SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_SERVER_URL, int(EMAIL_PORT_NUMBER)) as smtp_server:
            smtp_server.ehlo()
            smtp_server.starttls(context=context)
            smtp_server.ehlo()
            smtp_server.login(FROM_EMAIL, FROM_PASSWORD)
            smtp_server.send_message(msg)
            st.success(f"Email sent to {FROM_EMAIL}")
    except Exception as e:
        st.error(f"Error sending email: {e}")


# Main function
def main():
    st.title("Shipment Status Assistant")

    # Upload CSV files for Clients and Shipments
    st.subheader("Upload CSV Files")
    clients_file = st.file_uploader("Upload Clients CSV", type=['csv'])
    shipments_file = st.file_uploader("Upload Shipments CSV", type=['csv'])

    def load_data(clients_file, shipments_file):
        clients_data = pd.read_csv(clients_file)
        shipments_data = pd.read_csv(shipments_file, encoding='unicode_escape')
        return clients_data, shipments_data

    # Once files are uploaded, output the raw data
    client_name, shipment_id = "", ""
    if st.checkbox("Show Raw Data"):
        if clients_file is not None and shipments_file is not None:
            data_load_state = st.text("Loading data...")
            clients_df, shipments_df = load_data(clients_file, shipments_file)
            data_load_state.text("")

            st.subheader("Shipment Data")
            gb = GridOptionsBuilder.from_dataframe(shipments_df)
            gb.configure_selection(selection_mode="single", use_checkbox=True)
            grid_options = gb.build()
            shipments_response = AgGrid(
                shipments_df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=400,
                width='100%',
                enable_enterprise_modules=True
            )
            selected_row = shipments_response['selected_rows']
            if selected_row is not None:
                shipment_id = selected_row["ShipmentID"][0]
                client_id = selected_row["ClientID"][0]
                st.text_input("Shipment ID:", value=shipment_id, key="shipment_id_selected")
                st.text_input("Client ID:", value=client_id, key="client_id_selected")
            else:
                st.write("Please select a shipment to continue.")

    else:
        st.write("Please upload files to proceed. Recheck box once completed.")

    prompt = st.text_area(
        'Email Prompt: Please set the tone of your email.',
        height=100,
        max_chars=500,
        help='You can ask to write your emails in a different tone, style, or voice. Be specific.')

    # Get Client and Shipment info
    st.subheader("Submit Info and Send Email")
    if st.button("Submit"):
        if clients_file is not None and shipments_file is not None and prompt:
            try:
                # Fetch shipment status
                shipment_status, expected_delivery_date, client_name, client_email, \
                tracking_number, tracking_url, carrier = \
                    get_shipment_status(clients_df, shipments_df, client_id, shipment_id)
                # Send email
                if shipment_status:
                    send_email(expected_delivery_date, client_name, client_email, prompt, shipment_id,
                               tracking_number, tracking_url, carrier)
                    st.text("Shipment update successfully emailed to the client!")
                else:
                    st.warning(f"No shipment found for {client_name} with {shipment_id}")

            except Exception as e:
                st.error(f"Error processing files: {e}")


if __name__ == "__main__":
    main()
