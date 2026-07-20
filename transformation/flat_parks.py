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
    # header += flatten_json(camp.get("", {}), prefix="metadata")
    header.append(f"description: {camp.get('description')}")
    header.append(f"attractions: {camp.get('attractions')}")
    header.append(f"accommodation: {camp.get('accomodations')}")
    # header.append(f"accommodation_site: {camp.get('accomodations').values()}")

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
    chunks = build_chunks_from_file("data/clean_data/parks_data.json")
    
    with open("data/gold_data/parks.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- campsite details {i} ---\n")
            file.write(f"{chunk}\n\n")
        