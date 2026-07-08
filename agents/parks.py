import requests
import re
from bs4 import BeautifulSoup

def get_parks():

    url = "https://kws.go.ke/wp-json/wp/v2/pages/3837"
    headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

    resp = requests.get(url, headers=headers, timeout=15, verify=False)
    resp.raise_for_status()
    data = resp.json()

    # The rendered HTML content lives here in WP REST API responses
    html_content = data.get("content", {}).get("rendered", "")

    soup = BeautifulSoup(html_content, "html.parser")

    park_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("https://kws.go.ke/park/"):
            park_links.append(href)

    # Deduplicate while preserving order
    park_links = list(dict.fromkeys(park_links))

    for link in park_links:
        print(link)

    print(f"\nTotal park links found: {len(park_links)}")
    return park_links

# get_parks()