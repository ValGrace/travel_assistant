import pandas as pd

def transform_hotels():
    df = pd.read_json(
    "data/clean_data/kenyan_hotels.json"
)
    df["lat_round"] = df["lat"].round(4)
    df["lng_round"] = df["lng"].round(4)
    df["name"] = df["metadata"].apply(lambda m: m.get("name"))
    df["phone"] = df["metadata"].apply(lambda m: m.get("phone", ""))
    df["rating"] = df["metadata"].apply(lambda m: m.get("stars", 0))
    df["city"] = df["metadata"].apply(lambda m: m.get("addr:city"))
    df["street"] = df["metadata"].apply(lambda m: m.get("addr:street"))
    # df["website"] = df["metadata"].apply(lambda m: m.get("website"))



    duplicates_by_coords = df[df.duplicated(["name","lat_round", "lng_round"], keep=False)]
    df = df.drop_duplicates(subset=["name", "lat_round", "lng_round"], keep="first")
    df = df.drop(columns=["source", "metadata", "lng", "lat"], errors="ignore")
    df = df.dropna(subset=["name"])
    df_unique = df

    print(f"\n{'='*60}")
    print(f"DATASET OVERVIEW")
    print(f"{'='*60}")
    print(f"Rows:       {df_unique.shape[0]:,}")
    print(f"Columns:    {df_unique.shape[1]}")
    print(df_unique.head(5))

transform_hotels()