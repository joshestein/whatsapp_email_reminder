#!/usr/bin/env python3

import smtplib
import ssl
import time
from datetime import date, datetime, timedelta
from email.message import EmailMessage

from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def parse_date(date: str):
    try:
        return datetime.strptime(date, "%d/%m/%Y").date()
    except ValueError:
        return date


def get_contacts(driver):
    driver.get("https://web.whatsapp.com")

    # Wait until the page is loaded, by checking for search box
    WebDriverWait(driver, 50).until(lambda d: d.find_element("xpath", "//div[contains(., 'Search or start new chat')]"))
    side_panel = driver.find_element(By.ID, 'pane-side')

    contacts = {}
    cutoff = False

    # TODO: make configurable
    cutoff_date = date.today() - timedelta(weeks=3)
    while not cutoff:
        rows = side_panel.find_elements('xpath', ".//div[@role='row' and @tabindex='-1' and @aria-selected='false']")
        for row in rows:
            data = row.find_elements('xpath', ".//div[@aria-colindex='2']/div")
            parsed_date = parse_date(data[1].text)
            if isinstance(parsed_date, date) and parsed_date < cutoff_date:
                cutoff = True
                break

            if row.find_elements('xpath', ".//span[contains(@aria-label, 'unread')]"):
                data = row.text.split('\n')
                if data[0] not in contacts:
                    # TODO: save 'message'?
                    contacts[data[0]] = {'date': data[1]}

        # We scroll bit-by-bit until the cutoff date, or until we reach the end of the list
        end_of_scroll = driver.execute_script("""
            const sidepanel = arguments[0];
            sidepanel.scrollTop += sidepanel.offsetHeight;
            return sidepanel.scrollTop === sidepanel.scrollTopMax;
        """, side_panel)

        if end_of_scroll:
            break

        # Wait for scroll to finish
        time.sleep(0.5)

    return contacts


def email_reminders(contacts):
    config = dotenv_values()
    email = config['EMAIL']
    password = config['PASSWORD']

    message = EmailMessage()
    message["Subject"] = "Reminder to reply to your WhatsApp contacts"
    message["From"] = email
    message["To"] = email

    body = HTML_head()
    body += """
            You should reply to the following:<br><br>
            <table>
                <tr>
                <th>Name</th>
                <th>Last messaged</th>
                </tr>
    """

    for name, data in contacts.items():
        body += f'<tr><td>{name}</td><td>{data["date"]}</td></tr>'
    body += "</table>"
    body += HTML_tail()

    message.set_content(body, subtype='html')

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.ehlo()
        server.login(email, password)
        server.send_message(message)


def HTML_head():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your contacts</title>
            <style>
                table {
                    border: solid 1px lightgray;
                    border-collapse: collapse;
                    border-spacing: 0;
                    font: normal 14px Roboto, sans-serif;
                }

                th, td {
                    border: solid 1px lightgray;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
    """


def HTML_tail():
    return """
        </body>
    </html>
    """


if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=chrome-data")
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    contacts = get_contacts(driver)
    email_reminders(contacts)

    driver.close()
