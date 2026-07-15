import requests
import json, time
from bs4 import BeautifulSoup

def extract_places():
    def get_sign_xp():
        url = "https://magicalkenya.com/wp-json/wp/v2/adventures"
        headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        resp.raise_for_status()
        data = resp.json()
        getaways = []

        for data_xp in data:
            link = data_xp.get("link", "")
            title = data_xp.get("title", {}).get("rendered", ""),
            content = data_xp.get("content", {}).get("rendered", ""),
            excerpt = data_xp.get("excerpt", {}).get("rendered", ""),
            provider = data_xp.get("meta", {}).get("provided_by", ""),
            provider_website = data_xp.get("meta", {}).get("provider_website", ""),
            class_list = data_xp.get("class_list", [])
            getaways.append({
                "link": link,
                "title": title,
                "content": content,
                "excerpt": excerpt,
                "provided_by": provider,
                "website": provider_website,
                "class_list": class_list
            })
        with open("data/raw_data/mk_adventures.json", "a") as f:
            json.dump(getaways, f, indent=4)
    get_sign_xp()
extract_places()