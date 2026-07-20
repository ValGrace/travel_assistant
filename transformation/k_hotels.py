import pandas as pd
import json

def transform_hotels():
    df = pd.read_json(
    "data/raw_data/kenyan_campsites.json"
)
    df["latitude"] = df["lat"].round(4)
    df["longitude"] = df["lng"].round(4)
    df["name"] = df["metadata"].apply(lambda m: m.get("name"))
    # df["phone"] = df["metadata"].apply(lambda m: m.get("phone", ""))
    # df["rating"] = df["metadata"].apply(lambda m: m.get("stars", 0))
    # df["city"] = df["metadata"].apply(lambda m: m.get("addr:city"))
    # df["street"] = df["metadata"].apply(lambda m: m.get("addr:street"))
    # df["website"] = df["metadata"].apply(lambda m: m.get("website"))



    # duplicates_by_coords = df[df.duplicated(["name","latitude", "longitude"], keep=False)]
    df = df.drop_duplicates(subset=["name", "latitude", "longitude"], keep="first")
    df = df.drop(columns=["source", "lng", "lat"], errors="ignore")
    df = df.dropna(subset=["name"])
    df_unique = df

    print(f"\n{'='*60}")
    print(f"DATASET OVERVIEW")
    print(f"{'='*60}")
    print(f"Rows:       {df_unique.shape[0]:,}")
    print(f"Columns:    {df_unique.shape[1]}")
    print(df_unique.head(5))

    hotels_df = df.to_dict(orient="records")
    with open("data/clean_data/kenyan_campsites.json", "w", encoding="utf-8") as f:
        json.dump(hotels_df, f, indent=4, ensure_ascii=False)

transform_hotels()