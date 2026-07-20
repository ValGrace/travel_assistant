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

def hotel_chunks(hotel: dict) -> List[str]:
    header = [f"Hotel: {hotel.get('name')}"]
    # header += flatten_json(hotel.get("metadata", {}), prefix="metadata")
    header.append(f"type: {hotel.get('type')}")
    header.append(f"has_boat: {hotel.get('has_boat')}")
    header.append(f"has_vehicle: {hotel.get('has_vehicle')}")
    header.append(f"book_trip: {hotel.get('book_trip')}")

    chunks = []
    charges = hotel.get("entry_charges", {}).get("entry_charges", [])
    if charges:
        for acc in charges:
            chunk_lines = header.copy()
            chunk_lines.append("entry_charges")
            chunk_lines += flatten_json(acc, prefix="entry_charges")
            chunks.append("\n".join(chunk_lines))
    else:
        chunks.append("\n".join(header))
    activity_charges = hotel.get("listed_activity_charges", {}).get("listed_activity_charges", [])
    if activity_charges:
        for acc in activity_charges:
            chunk_lines = header.copy()
            chunk_lines.append("listed_activity_charges")
            chunk_lines += flatten_json(acc, prefix="listed_activity_charges")
            chunks.append("\n".join(chunk_lines))
    else:
        chunks.append("\n".join(header))

    return chunks

def build_chunks_from_file(path: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        hotels = json.load(f)
    all_chunks = []
    for hotel in hotels:
        all_chunks.extend(hotel_chunks(hotel))
    return all_chunks

if __name__ == "__main__":
    chunks = build_chunks_from_file("data/clean_data/kws_prices.json")
    
    with open("data/gold_data/kws_prices.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- kws pricing {i} ---\n")
            file.write(f"{chunk}\n\n")
        