from bs4 import BeautifulSoup
import requests

def safaris():
    url = "https://www.africansafarikenya.com/safaris/affordable-kenya-safaris"
    headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

    resp = requests.get(url, headers=headers, timeout=15, verify=False)
    resp.raise_for_status()
    data = resp.text
    print(data)
    safaris = []

safaris()