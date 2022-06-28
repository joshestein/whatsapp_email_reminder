#!/usr/bin/env python3

import smtplib
import ssl

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def get_contacts(driver):
    driver.get("https://web.whatsapp.com")

    # Wait until the page is loaded, by checking for search box
    WebDriverWait(driver, 50).until(lambda d: d.find_element("xpath", "//div[contains(., 'Search or start new chat')]"))

    unread = driver.find_elements(
        "xpath", "//span[contains(@aria-label, 'unread')]/ancestor::div[@role='row' and @tabindex='-1' and @aria-selected='false']")

    # TODO: scroll down to fetch more chats
    contacts = []
    for chat in unread:
        contact = chat.find_element("xpath", ".//div[@aria-colindex='2']")
        name, date = contact.text.split("\n")
        contacts.append((name, date))

    return contacts


def email_reminders(contacts):
    config = dotenv_values()
    email = config['EMAIL']
    password = config['PASSWORD']
    port = 465  # For SSL

    subject = "Reminder to reply to your WhatsApp contacts"
    body = f"Subject: {subject}\n\n"
    body += "You should reply to the following:\n\n"
    for contact in contacts:
        name, date = contact[0], contact[1]
        body += f"{name} - {date}\n"

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.ehlo()
        server.login(email, password)
        server.sendmail(email, email, body)


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir=chrome-data")
    driver = webdriver.Chrome(options=options)

    contacts = get_contacts(driver)
    email_reminders(contacts)

    driver.close()
