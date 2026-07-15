import requests
import json, time
from bs4 import BeautifulSoup

def extract_places():
    def get_places_links():
        url = "https://magicalkenya.com/wp-json/wp/v2/travel-category"
        headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        data = resp.json()
        links = []

        for category in data:
            travel_category = category.get("link", "")
            links.append(travel_category)
        return links
    def get_place(canonical):
        headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}
        response = requests.get(canonical, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        content = response.text

        soup = BeautifulSoup(content, "html.parser")
        places = []
        try:
            place_title = None
            for tag in soup.find_all("h1", class_="entry-title"):
                title = tag.find("span")
                if title:
                    place_title = title.get_text(strip=True)

            # Extract camps/articles under that place
            for article in soup.find_all("article", class_="post"):
                n_title = article.find("h2", class_="entry-title")
                descr = article.find("p")

                entry_title = n_title.get_text(strip=True) if n_title else None
                description = descr.get_text(strip=True) if descr else None

                if entry_title and description:
                    places.append({
                        "place": place_title,
                        "camps": {
                            "name": entry_title,
                            "description": description
                        }
                    })
            with open("data/raw_data/magicalkenya_categories.json", "a") as f:
                json.dump(places, f, indent=4)
        except Exception as e:
            print(f"Encountered an issue: {e}")
    
    links = get_places_links()
    for link in links:
        get_place(link)
        time.sleep(10)

            


extract_places()
