import json
from typing import Any, List

def flatten_json(obj: Any, prefix: str = "") -> List[str]:
    lines: List[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_prefix = f"{prefix}.{key}" if prefix else key
            lines.extend(flatten_json(value, new_prefix))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj, start=1):
            new_prefix = f"{prefix}[{idx}]"
            lines.extend(flatten_json(item, new_prefix))
    else:
        lines.append(f"{prefix}: {obj}")
    return lines

def camp_chunks(camp: dict) -> List[str]:
    header = [f"Hotel name: {camp.get('hotel_name')}"]
    header.append(f"website: {camp.get('hmn_url')}")
    header.append(f"address: {camp.get('address')}")
    header.append(f"description: {camp.get('description')}")
    header.append(f"currency: {camp.get('currency')}")
    header.append(f"price_from: {camp.get('price_from')}")
    header.append(f"rating: {camp.get('rating')}")

    chunks = []
    chunks.append("\n".join(header))
    

    return chunks

def build_chunks_from_file(path: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        campsites = json.load(f)
    all_chunks = []
    for camp in campsites:
        all_chunks.extend(camp_chunks(camp))
    return all_chunks

if __name__ == "__main__":
    chunks = build_chunks_from_file("data/clean_data/nai_hotels.json")
    
    with open("data/gold_data/nairobi_hotels.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- Nairobi hotels {i} ---\n")
            file.write(f"{chunk}\n\n")
        