import requests, json, time
from bs4 import BeautifulSoup
from parks import get_parks
def get_park_details(url):


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
    final_details = {
         "description": final_description,
         "attractions": attractions,
         "accomodations": accommodations
    }
    with open("data/raw_data/parks_data.json", "a") as f:
        json.dump(final_details, f, indent=4)

# url = "https://kws.go.ke/park/sibiloi-national-park/"

park_links = get_parks()
for url in park_links:
    try:

        get_park_details(url)
        time.sleep(10)
    except Exception as e:
        print(f"Failed to scrape because: {e}")
        continue


