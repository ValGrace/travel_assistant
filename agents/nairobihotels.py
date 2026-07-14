import requests
import json
from bs4 import BeautifulSoup

url = "https://www.hotelsmixnairobi.com/en/search/10/"

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
        address = None
        description = None
        prices = None

        # Example: look for sibling/parent elements that contain extra info
        addr_tag = title.find_next("p")
        if addr_tag:
            address = addr_tag.get_text(strip=True)

        price_tag = title.find_next("i")
        if price_tag:
            prices = price_tag.get_text(strip=True)
        
        descr_tags = tag.find_all("div", class_="hotel-text")
        description = " ".join(d.get_text(strip=True) for d in descr_tags)

        accommodations.append({
            "hotel_name": hotel_name,
            "url": href,
            "address": address,
            "description": description,
            "prices": prices
        })

print(accommodations)
with open("data/raw_data/nairobi_hotels.json", "a") as f:
        json.dump(accommodations, f, indent=4)
