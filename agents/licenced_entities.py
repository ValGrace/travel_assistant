import requests
from bs4 import BeautifulSoup

url = "https://tra.go.ke/licencing-2/list-of-entities"

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
                "class": cols[1].get_text(strip=True),
                "company_name": cols[2].get_text(strip=True),
                "location": cols[3].get_text(strip=True),
                "county": cols[4].get_text(strip=True),
                "town": cols[5].get_text(strip=True),
                "service_name": cols[6].get_text(strip=True),
            }
            rows_data.append(row_dict)

print(rows_data)
