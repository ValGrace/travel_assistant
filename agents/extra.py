import requests
from bs4 import BeautifulSoup
import json

headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

def scrape_ld_json_hotel(url):
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {}

    soup = BeautifulSoup(resp.text, "html.parser")
    scripts = soup.find_all("script", type="application/ld+json")

    hotels = []
    for script in scripts:
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = data.get("@graph", [data]) if isinstance(data, dict) else data
        for item in candidates:
            if isinstance(item, dict) and item.get("@type") == "Hotel":
                hotels.append(item)

    return hotels if hotels else {}

url = "https://www.hyatt.com/hyatt-place/en-US/nbozn-hyatt-place-nairobi-westlands/rooms"
raw = scrape_ld_json_hotel(url)

print(json.dumps(raw, indent=2))
