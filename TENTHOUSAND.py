from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

service = Service(os.getenv("CHROME_DRIVER_PATH"))
options = Options()
options.add_argument('--headless=new')
driver = webdriver.Chrome(service=service, options=options)

def check_availability():
    print("Checking availability...")
    driver.get(os.getenv("BOOKING_URL"))
    time.sleep(5)  # Give the page time to load dynamically loaded content

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    booking_slots = soup.find_all('button', class_='ember-power-calendar-day ember-power-calendar-day--interactive ember-power-calendar-day--current-month', disabled=False)

    return len(booking_slots)

def send_email(subject, body):
    sender_email = os.getenv("EMAIL_ADDRESS")
    receiver_email = os.getenv("RECEIVER_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, [sender_email, receiver_email], text)
        server.quit()
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")

try:
    initial_slots = check_availability()
    interval = 300  # 5 minutes

    while True:
        current_slots = check_availability()
        if current_slots > initial_slots:
            print("New booking slots available!")
            subject = "👉🏻 BOOK NOW 👈🏻"
            body = "New booking slots available! There are now " + str(current_slots) + " slots"            
            send_email(subject, body)
            initial_slots = current_slots 
        else:
            print("No new slots available — there are currently", current_slots, "slots")
        
        time.sleep(interval)
finally:
    driver.quit()