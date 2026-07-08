import requests
from bs4 import BeautifulSoup
import json

headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

def scrape_ld_json_hotel(url):
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")

    scripts = soup.find_all("script", type="application/ld+json")

    hotel_data = None
    for script in scripts:
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        # Some sites wrap types in @graph, others put Hotel directly at top level
        candidates = data.get("@graph", [data]) if isinstance(data, dict) else data

        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "Hotel":
                hotel_data = item
                break
        if hotel_data:
            print(hotel_data)

    return hotel_data


url = "https://www.hyatt.com/hyatt-place/en-US/nbozn-hyatt-place-nairobi-westlands/rooms"
raw = scrape_ld_json_hotel(url)
print(raw)
print(json.dumps(raw, indent=2))