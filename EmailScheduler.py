import pandas as pd
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.blocking import BlockingScheduler
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")
FROM_PASSWORD = os.getenv("FROM_PASSWORD")
EMAIL_SERVER_URL = os.getenv("EMAIL_SERVER_URL")
EMAIL_PORT_NUMBER = int(os.getenv("EMAIL_PORT_NUMBER"))
FILE_TO_READ = os.getenv("FILE_TO_READ")
EMAIL_FREQUENCY = 24  # IN HOURS


# Read and Process CSV files
def read_csv(file_path):
    return pd.read_csv(file_path), pd.read_csv(file_path)


def get_billing_info(user, billing, query):
    user_info = user.query(query)
    billing_info = billing.query(query)
    return user_info, billing_info


# Generate Customized Emails using ChatGPT
def generate_email(content):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": content}
        ]
    )
    return response.choices[0].messages['content']


# Send Emails
def send_email(subject, body, to_email):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject  # TODO

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(EMAIL_SERVER_URL, EMAIL_PORT_NUMBER)
    server.starttls()
    server.login(FROM_EMAIL, FROM_PASSWORD)
    text = msg.as_string()
    server.sendmail(FROM_EMAIL, to_email, text)
    server.quit()


# Automate the Emails
def scheduled_task():
    df, df2 = read_csv(FILE_TO_READ)
    user_info, billing_info = get_billing_info(df, df2, "query")  # TODO
    email_subject, email_body = generate_email(f"Extracted information: {user_info}")
    send_email(email_subject, email_body, user_info)


scheduler = BlockingScheduler()
scheduler.add_job(scheduled_task, 'interval', hours=EMAIL_FREQUENCY)
scheduler.start()
