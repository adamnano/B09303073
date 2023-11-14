import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import random
import time


base_url = "https://www.booking.com/searchresults.html?ss=Taichung&checkin_year_month_monthday=2023-12-15&checkout_year_month_monthday=2023-12-18&rows=25&offset=350"

response = requests.get(base_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'})
soup = BeautifulSoup(response.content, 'html.parser')

hotel = soup.find_all("div", class_="c82435a4b8 a178069f51 a6ae3c2b40 a18aeea94d d794b7a0f7 f53e278e95 c6710787a4")

hotel = hotel[0].find("div", class_="f6431b446c a15b38c233").get_text(strip=True)

print(hotel)