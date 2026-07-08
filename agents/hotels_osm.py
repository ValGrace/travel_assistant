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
            way["tourism"="hotel"][rooms](if:t["rooms"]>2)(area.searchArea);
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
        osm_hotels = []
        for elem in osm_data['elements']:
            if "lat" in elem:
                lat, lng = elem["lat"], elem["lon"]
            elif "center" in elem:
                lat, lng = elem["center"]["lat"], elem["center"]["lon"]
            else:
                continue
            osm_hotels.append({
                "hotel_name": elem.get("tags", {}).get("name", "Unknown"),
                "phone": elem.get("tags", {}).get("phone", ""),
                "tourism": elem.get("tags", {}).get("tourism", ""),
                "website": elem.get("tags", {}).get("website", ""),
                "city": elem.get("tags", {}).get("addr:city", ""),
                "street": elem.get("tags", {}).get("addr:street", ""),
                "housenumber": elem.get("tags", {}).get("addr:housenumber", ""),
                "postcode": elem.get("tags", {}).get("addr:postcode", ""),
                "email": elem.get("tags", {}).get("email", ""),
                "rating": elem.get("tags", {}).get("stars", "no rating"),
                "amenities": {
                    "internet_access": elem.get("tags", {}).get("internet_access", "unspecified"),
                    "internet_access_fee": elem.get("tags", {}).get("internet_access:fee", ""),
                    "wheelchair": elem.get("tags", {}).get("wheelchair", ""),
                    "air_conditioning": elem.get("tags", {}).get("air_conditioning", "not needed"),
                    "bar": elem.get("tags", {}).get("bar", "no"),
                    "smoking": elem.get("tags", {}).get("smoking", "not specified"),
                    "swimming_pool": elem.get("tags", {}).get("swimming_pool", "")
                },
                "reservation": elem.get("tags", {}).get("reservation", "no"),
                "rooms": elem.get("tags", {}).get("rooms", ""),
                "lat": lat,
                "lng": lng,
                "source": "osm"
            })

    
    scrape_osm()

extract()