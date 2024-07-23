import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def extract_info(content):
    date_pattern = r'\d{2}/\d{2}/\d{2}'
    time_pattern = r'\d{2}:\d{2}'

    date_match = re.search(date_pattern, content)
    date = date_match.group(0) if date_match else None

    time_match = re.search(time_pattern, content)
    time = time_match.group(0) if time_match else None

    description = re.sub(date_pattern, '', content)
    description = re.sub(time_pattern, '', description).strip()

    location = 'Unknown'
    if 'Gaza' in description:
        location = 'Gaza'
    elif 'Lebanon' in description:
        location = 'Lebanon'
    elif 'Israel' in description:
        location = 'Israel'

    return {
        'Date': date,
        'Time': time,
        'Location': location,
        'Description': description
    }


driver = webdriver.Chrome()

try:
    driver.get("https://www.idf.il/en/mini-sites/hamas-israel-war-24/real-time-updates/")

    timeout = 10

    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.content-wrapper"))
    )

    rendered_html = driver.page_source

    soup = BeautifulSoup(rendered_html, features="html.parser")

    start_tag = soup.find('h2', string='14/10/23')

    if start_tag:
        collected_content = []
        current = start_tag
        while current:
            collected_content.append(current)
            current = current.find_next_sibling()

        data = []
        date = None
        for element in collected_content:
            if element.name == 'h2':
                date = element.get_text(strip=True)
            elif element.name == 'p':
                info = extract_info(element.get_text(separator=' ', strip=True))
                if date:
                    info['Date'] = date
                data.append(info)

        df = pd.DataFrame(data)
        df.to_csv('idf_report.csv', index=False)
        print("Data saved to idf_report.csv")

    else:
        print("Starting tag '14/10/23' not found.")
finally:
    driver.quit()
