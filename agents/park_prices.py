import requests
import json

def dest_prices():

    kws_destinations = requests.get("https://kwspay.ecitizen.go.ke/api/kws/destinations")

    kws_data = kws_destinations.json()

    with open("data/raw_data/kws_prices.json", "w") as f:
        json.dump(kws_data, f, indent=4)

dest_prices()