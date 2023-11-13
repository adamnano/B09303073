from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import random
import time

def fetch_hotel_data(location, checkin_date, checkout_date):
    # Format the dates
    checkin_date = datetime.strptime(checkin_date, "%Y-%m-%d").strftime("%Y-%m-%d")
    checkout_date = datetime.strptime(checkout_date, "%Y-%m-%d").strftime("%Y-%m-%d")

    # URL construction
    url = f"https://www.booking.com/searchresults.html?ss={location}&checkin_year_month_monthday={checkin_date}&checkout_year_month_monthday={checkout_date}"

    # Setting up WebDriver
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
        # ... Your user agents here
    ]
    options = Options()
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    #options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    hotels = []
    while True:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "c066246e13")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract hotel data
        for hotel_box in soup.find_all("div", class_="c066246e13"):
            name = hotel_box.find('div', class_='f6431b446c a15b38c233').get_text(strip=True) if hotel_box.find('div', class_='f6431b446c a15b38c233') else "No Name"
            rating = hotel_box.find("div", class_="a3b8729ab1 d86cee9b25").get_text(strip=True) if hotel_box.find("div", class_="a3b8729ab1 d86cee9b25") else "No Rating"
            distance = hotel_box.find("span", {"data-testid": "distance"}).get_text(strip=True) if hotel_box.find("span", {"data-testid": "distance"}) else "No Distance"

            hotels.append({"Name": name, "Rating": rating, "Distance": distance})

        # Check for next page button
        next_button = driver.find_elements(By.CLASS_NAME, "a83ed08757 c21c56c305 f38b6daa18 d691166b09 ab98298258 deab83296e bb803d8689 a16ddf9c57")
        if not next_button:
            break  # Exit loop if no next page button is found
        else:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "a83ed08757")))
            next_button[0].click()
            time.sleep(3)  # Wait for the next page to load

    driver.quit()
    return pd.DataFrame(hotels)

# Example usage
df = fetch_hotel_data("Taichung", "2023-11-15", "2023-11-18")
print(df[:40])

