import requests, json, time

def extract():
    def scrape_osm():
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = """
            [out:json][timeout:900];
            area(3600192798)->.kenya;
            area["ISO3166-1"="KE"][admin_level=2]->.searchArea;
            (
            node["tourism"="hotel"](area.searchArea);
            way["tourism"="hotel"](area.searchArea);
            );
            out center tags;
   
                """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "hotels-research/1.0"
        }
        r = requests.post(overpass_url, data={"data": query}, headers=headers)
        r.raise_for_status()
        
        osm_data = r.json()
        print(f"Found {len(osm_data['elements'])} elements")
        osm_campsites = []
        osm_urls = []
        for elem in osm_data['elements']:
            if "lat" in elem:
                lat, lng = elem["lat"], elem["lon"]
            elif "center" in elem:
                lat, lng = elem["center"]["lat"], elem["center"]["lon"]
            else:
                continue
            osm_campsites.append({
                "metadata": elem.get("tags", {}),
                "lat": lat,
                "lng": lng,
                "source": "osm"
            })
            website = elem.get("tags", {}).get("website", "")
            if website:
                osm_urls.append(website)
        # with open("data/raw_data/kenyan_hotels.json", "w") as f:
        #     json.dump(osm_campsites, f, indent=4)

        print(osm_urls)
        return osm_urls
    
    scrape_osm()

extract()