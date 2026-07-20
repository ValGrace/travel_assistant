import pandas as pd
import json

def build_entry_charges(charges):
    if not isinstance(charges, list):
        return []
    entries = []
    for d in charges:
        category = d.get("name", "")
        for s in d.get("services", []):
            entries.append({
                "category": category,
                "description": s.get("description", ""),
                "currency": s.get("currency", ""),
                "price": s.get("prices")
            })
    return entries

def transform_kwsprices():
    df = pd.read_json(
    "data/raw_data/kws_prices.json"
)
    new_df = pd.DataFrame()
    # df["config"] = df["config"]
    new_df["name"] = df["name"]
    new_df["type"] = df["type"]
    # df["entrance_gates"] = df["entranceGates"]
    new_df["entry_charges"] = df["entryCharges"].apply(
    lambda charges: {"entry_charges": build_entry_charges(charges)}
)
    new_df["listed_activity_charges"] = df["listedActivities"].apply(
    lambda charges: {"listed_activity_charges": build_entry_charges(charges)}
)
    
    
    new_df["has_boat"] = df["hasBoat"]
    new_df["has_vehicle"] = df["hasVehicle"]
    new_df["book_trip"] = "https://kwspay.ecitizen.go.ke" + df["href"]
   
    # new_df["modes_of_transport"] = df["modesOfTransport"]

    df_unique = new_df
    print(f"\n{'='*60}")
    print(f"DATASET OVERVIEW")
    print(f"{'='*60}")
    print(f"Rows:       {df_unique.shape[0]:,}")
    print(f"Columns:    {df_unique.shape[1]}")
    print(df_unique.head(5))

    kws_df = new_df.to_dict(orient="records")
    with open("data/clean_data/kws_prices.json", "w", encoding="utf-8") as f:
        json.dump(kws_df, f, indent=4, ensure_ascii=False)

transform_kwsprices()
    
