import requests, json, time

def extract():
    def scrape_osm():
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = """
            [out:json][timeout:900];
            area(3600192798)->.kenya;
            area["ISO3166-1"="KE"][admin_level=2]->.searchArea;
            (
            node["tourism"="camp_site"](area.searchArea);
            way["tourism"="camp_site"](area.searchArea);
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
        for elem in osm_data['elements']:
            if "lat" in elem:
                lat, lng = elem["lat"], elem["lon"]
            elif "center" in elem:
                lat, lng = elem["center"]["lat"], elem["center"]["lon"]
            else:
                continue
            osm_campsites.append({
                "camp_name": elem.get("tags", {}).get("name", "Unknown"),
                "phone": elem.get("tags", {}).get("phone", ""),
                "tourism": elem.get("tags", {}).get("tourism", ""),
                "website": elem.get("tags", {}).get("website", ""),
                "city": elem.get("tags", {}).get("addr:city", ""),
                "street": elem.get("tags", {}).get("addr:street", ""),
                "email": elem.get("tags", {}).get("email", ""),
                "rating": elem.get("tags", {}).get("stars", "no rating"),
                "amenities": {
                    "internet_access": elem.get("tags", {}).get("internet_access", "unspecified"),
                    "tents": elem.get("tags", {}).get("tents", ""),
                    "cabins": elem.get("tags", {}).get("cabins", ""),
                    "openfire": elem.get("tags", {}).get("openfire", ""),
                    "toilets": elem.get("tags", {}).get("toilets", ""),
                    "smoking": elem.get("tags", {}).get("smoking", ""),
                    "drinking_water": elem.get("tags", {}).get("drinking_water", ""),
                    "amenity": elem.get("tags", {}).get("amenity", ""),
                    "power_supply": elem.get("tags", {}).get("power_supply", "not specified"),
                    "caravans": elem.get("tags", {}).get("caravans", ""),
                   
                },
                "lat": lat,
                "lng": lng,
                "source": "osm"
            })
        with open("data/raw_data/kenyan_campsites.json", "w") as f:
            json.dump(osm_campsites, f, indent=4)

        print(osm_data)

    
    scrape_osm()

extract()