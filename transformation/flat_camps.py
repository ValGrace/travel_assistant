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
    header = [f"Campsite: {camp.get('name')}"]
    header += flatten_json(camp.get("metadata", {}), prefix="metadata")
    header.append(f"latitude: {camp.get('latitude')}")
    header.append(f"longitude: {camp.get('longitude')}")

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
    chunks = build_chunks_from_file("data/clean_data/kenyan_campsites.json")
    
    with open("data/gold_data/kenyan_campsites.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- campsite details {i} ---\n")
            file.write(f"{chunk}\n\n")
        