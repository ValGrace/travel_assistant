import pandas as pd
import re
import json

df = pd.read_json(
    "data/raw_data/nairobi_hotels.json"
)

def extract_rating(text):
    if not isinstance(text, str):
        return 0
    match = re.search(r'(\d+)-star', text)
    return int(match.group(1)) if match else 0

def split_price(price_str):
    if not isinstance(price_str, str):
        return "", ""
    
    match = re.match(r"([A-Za-z]+)\s*([\d,]+)", price_str)
    if match:
        currency = match.group(1)
        amount = int(match.group(2).replace(",", ""))
        return currency, amount
    return "", ""

df[["currency", "price_from"]] = df["prices"].apply(lambda x: pd.Series(split_price(x)))

df["ratings"] = df["description"].apply(extract_rating)

nai_hotels = df.to_dict(orient="records")

with open("data/clean_data/nai_hotels.json", "w", encoding="utf-8") as f:
    json.dump(nai_hotels, f, indent=4, ensure_ascii=False)
print(df.head(20))