import requests, json
from bs4 import BeautifulSoup

url = "https://web.archive.org/web/20260313055117/https://tra.go.ke/licensing-2/list-of-entities/"

headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

resp = requests.get(url, headers=headers, timeout=15, verify=False)
resp.raise_for_status()
content= resp.text

soup = BeautifulSoup(content, "html.parser")

rows_data = []

for tag in soup.find_all("table", class_="tablepress-id-3"):
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if cols:
            row_dict = {
                "file_number": cols[0].get_text(strip=True),
                "company_name": cols[1].get_text(strip=True),
                "town": cols[2].get_text(strip=True),
                "service_category_name": cols[3].get_text(strip=True),
                        }
            rows_data.append(row_dict)

with open("data/raw_data/entities.json", "w") as f:
        json.dump(rows_data, f, indent=4)
