import requests

kws_destinations = requests.get("https://kwspay.ecitizen.go.ke/api/kws/destinations")

print(kws_destinations.json())