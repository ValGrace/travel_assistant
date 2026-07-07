import requests
from bs4 import BeautifulSoup

url = "https://kws.go.ke/park/sibiloi-national-park/"

headers = {"User-Agent": "Mozilla/5.0 (research data collection)"}

resp = requests.get(url, headers=headers, timeout=15, verify=False)
resp.raise_for_status()
content= resp.text

soup = BeautifulSoup(content, "html.parser")

# for child in soup.descendants:
#     print(child.name)

description = []

for tag in soup.find_all("div", class_="fusion-text-2"):
    for p in tag.find_all("p"):
        text = p.get_text(strip=True)
        description.append(text)
    
    
final_description = " ".join(description)
print(final_description)

attractions = []
for tag in soup.select(".tab-content"):
    for attr in tag.find_all("li", attrs={'aria-level': '1'}):
        text = attr.get_text(strip=True)
        attractions.append(text)

print(attractions)

accommodations = {}
for tag in soup.find_all("div", class_="fusion-clearfix", attrs={'aria-labelledby': 'fusion-tab-accommodation'}):
    for lnk in tag.find_all('a', href=True):
        hotel_name = lnk.get_text(strip=True)   # visible text of the link
        href = lnk["href"]
        accommodations[hotel_name] = href

print(accommodations)

