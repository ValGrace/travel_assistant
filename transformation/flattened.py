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
    header += flatten_json(hotel.get("metadata", {}), prefix="metadata")
    header.append(f"latitude: {hotel.get('latitude')}")
    header.append(f"longitude: {hotel.get('longitude')}")

    chunks = []
    accommodations = hotel.get("accommodations", [])
    if accommodations:
        for acc in accommodations:
            chunk_lines = header.copy()
            chunk_lines.append("accommodation:")
            chunk_lines += flatten_json(acc, prefix="accommodation")
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
    chunks = build_chunks_from_file("data/clean_data/kenyan_hotels.json")
    
    with open("data/gold_data/kenyan_hotels.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- hotel details {i} ---\n")
            file.write(f"{chunk}\n\n")
        