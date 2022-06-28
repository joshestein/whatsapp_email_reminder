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

    row_attributes = "div[@role='row' and @tabindex='-1' and @aria-selected='false']"
    side_panel = driver.find_element(By.ID, 'pane-side')
    rows = side_panel.find_elements('xpath', f".//{row_attributes}")

    contacts = {}
    for row in rows:
        if row.find_elements('xpath', f".//span[contains(@aria-label, 'unread')]"):
            data = row.text.split('\n')
            contacts[data[0]] = {'date': data[1]}
            # TODO: save 'message'?
            # contacts[data[0]] = {'date': data[1], 'message': data[2]}

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

        new_rows = side_panel.find_elements('xpath', f".//{row_attributes}")
        for row in new_rows:
            data = row.find_elements('xpath', f".//div[@aria-colindex='2']/div")
            if row.find_elements('xpath', f".//span[contains(@aria-label, 'unread')]"):
                data = row.text.split('\n')
                if data[0] not in contacts:
                    contacts[data[0]] = {'date': data[1]}

    return contacts


def email_reminders(contacts):
    config = dotenv_values()
    email = config['EMAIL']
    password = config['PASSWORD']

    subject = "Reminder to reply to your WhatsApp contacts"
    body = f"Subject: {subject}\n\n"
    body += "You should reply to the following:\n\n"
    for name, data in contacts.items():
        body += f"{name} - {data['date']}\n"

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
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
