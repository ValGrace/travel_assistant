import requests, json, time
from bs4 import BeautifulSoup
import requests, json
from bs4 import BeautifulSoup

url = "https://uk.hotels.com/Hotel-Search?regionId=2523&destination=Nairobi%2C%20Nairobi%20County%2C%20Kenya&selected=32868230&adults=2&children=&sort=RECOMMENDED&useRewards=false&semdtl=&userIntent=&vip=false&startDate=2026-07-23&endDate=2026-07-24&theme=&categorySearch="

headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

resp = requests.get(url, headers=headers, timeout=15, verify=False)
resp.raise_for_status()
content= resp.text


soup = BeautifulSoup(content, "html.parser")

accommodations = []

for tag in soup.find_all("div", class_="hotels-list__item"):
    for title in tag.find_all('a', href=True):
        hotel_name = title.get_text(strip=True)
        href = title['href']
        # Try to extract description and price if available
        description = None
        prices = None

        # Example: look for sibling/parent elements that contain extra info
        desc_tag = title.find_next("p")
        if desc_tag:
            description = desc_tag.get_text(strip=True)

        price_tag = title.find_next("i")
        if price_tag:
            prices = price_tag.get_text(strip=True)

        accommodations.append({
            "hotel_name": hotel_name,
            "url": href,
            "description": description,
            "prices": prices
        })

print(accommodations)
