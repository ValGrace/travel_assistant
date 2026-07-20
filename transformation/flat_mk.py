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

def getaway_chunks(getaway: dict) -> List[str]:
    header = [f"Getaway Ideas: {getaway.get('title')}"]
    header.append(f"website: {getaway.get('website')}")
    header.append(f"link: {getaway.get('link')}")
    header.append(f"description: {getaway.get('content')}")
    header.append(f"about: {getaway.get('class_list')}")
  

    chunks = []
    chunks.append("\n".join(header))
    

    return chunks
def adventure_chunks(adventure: dict) -> List[str]:
    header = [f"Adventure: {adventure.get('title')}"]
    header.append(f"website: {adventure.get('link')}")
    header.append(f"description: {adventure.get('content')}" )
    header.append(f"category: {adventure.get('class_list')}")

    chunks = []
    chunks.append("\n".join(header))
    return chunks

def places_chunks(places: dict) -> List[str]:
    header = [f"Places: {places.get('name')}"]
    header.append(f"places: {places.get('places')}")
    header.append(f"description: {places.get('description')}")

    chunks = []
    chunks.append("\n".join(header))
    return chunks


def category_chunks(category: dict) -> List[str]:
    header = ["Magical Kenya Destination Camps \n"]
    header.append(f"place: {category.get("place")}")
    header.append(f"name: {category.get("camps").get("name")}")
    header.append(f"description: {category.get("camps").get("description")}")

    chunks = []
    chunks.append("\n".join(header))
    return chunks


def build_chunks_from_file(path: str, path2: str, path3: str, path4: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        getaways = json.load(f)
    all_chunks = []
    for getaway in getaways:
        all_chunks.extend(getaway_chunks(getaway))
    
    with open(path2, encoding="utf-8") as f:
        adventures = json.load(f)
    for adventure in adventures:
        all_chunks.extend(adventure_chunks(adventure))
    with open(path3, encoding="utf-8") as f:
        places = json.load(f)
    for place in places:
        all_chunks.extend(places_chunks(place))
    
    with open(path4, encoding="utf-8") as f:
        categories = json.load(f)
    for category in categories:
        all_chunks.extend(category_chunks(category))
    return all_chunks

if __name__ == "__main__":
    chunks = build_chunks_from_file("data/raw_data/mk_getaways.json", "data/raw_data/mk_adventures.json", "data/raw_data/magicalkenya_places.json", "data/raw_data/magicalkenya_categories.json")
    
    with open("data/gold_data/magical_kenya.txt", "a", encoding="utf-8") as file:
        for i, chunk in enumerate(chunks, 1):
            file.write(f"--- Magical Kenya Adventures {i} ---\n")
            file.write(f"{chunk}\n\n")
        