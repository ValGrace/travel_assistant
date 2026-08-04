"""Small, dependency-free retrieval layer for the Kenya travel knowledge base."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus


def _normalize_value(value: str) -> str:
    value = value.strip()
    if value.lower() in {"none", "null", ""}:
        return ""
    if value.startswith("[") or value.startswith("{"):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, dict):
                return ", ".join(f"{k}: {v}" for k, v in parsed.items())
            if isinstance(parsed, (list, tuple)):
                return ", ".join(str(item) for item in parsed if item is not None)
        except (ValueError, SyntaxError):
            pass
    return value


def _field(text: str, *names: str) -> str | None:
    """Return the first non-empty value for one of the line-oriented fields."""
    for name in names:
        pattern = rf"^{re.escape(name)}:\s*(.+)$"
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            value = _normalize_value(match.group(1))
            if value:
                return value
    return None


def _friendly_label(key: str) -> str:
    key = re.sub(r"\[\d+\]", "", key).replace("_", " ").replace(".", " ")
    return re.sub(r"\s+", " ", key).strip().title()


def _travel_facts(text: str, metadata: dict) -> str:
    """Convert flattened fields and JSON metadata into model-readable travel facts."""
    ignored = {"source", "record index", "record number", "chunk type", "chunk start", "start"}
    facts: list[str] = []
    for key, value in metadata.items():
        label = _friendly_label(key)
        if label.lower() not in ignored and value not in (None, "", "None"):
            facts.append(f"{label}: {value}")
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        label, value = _friendly_label(key), value.strip()
        if label.lower() not in ignored and value and value not in {"None", "null"}:
            facts.append(f"{label}: {value}")
    # Preserve order while removing repeated key/value pairs.
    return "\n".join(dict.fromkeys(facts))


def _natural_details(document: "TravelDocument", metadata: dict | None = None) -> tuple[str, str | None]:
    """Turn raw extraction fields into a short, readable travel recommendation."""
    text = document.text
    description = _field(text, "description", "accommodation.description")
    address = _field(text, "address")
    room_type = _field(text, "accommodation.type")
    price = _field(text, "price_from", "accommodation.price_per_person")
    currency = _field(text, "currency", "accommodation.currency")
    amenities = re.findall(r"^accommodation\.amenities\[\d+\]:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    latitude = _field(text, "latitude")
    longitude = _field(text, "longitude")
    metadata = metadata or {}

    sentences: list[str] = []
    if description:
        sentences.append(description.rstrip(".") + ".")
    if address:
        sentences.append(f"It is located at {address}.")
    if room_type:
        sentences.append(f"The available stay listed here is a {room_type}.")
    if price:
        amount = f"{currency} {price}" if currency else price
        sentences.append(f"The listed rate starts from {amount}.")
    if amenities:
        cleaned = [item.strip().lstrip(":") for item in amenities[:4]]
        sentences.append(f"Useful amenities include {', '.join(cleaned)}.")
    if not sentences:
        kind = _field(text, "metadata.tourism") or metadata.get("chunk_type") or "place to stay"
        name = document.title.split(",")[0].strip()
        article = "an" if str(kind).lower()[:1] in "aeiou" else "a"
        sentences.append(f"{name} is listed as {article} {kind} in the Kenya travel collection.")
        if metadata.get("hotel"):
            sentences.append(f"It is associated with {metadata['hotel']}.")
        if latitude and longitude:
            sentences.append("Use the map to check its precise location and nearby attractions.")

    map_url = None
    if latitude and longitude:
        map_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(f'{latitude},{longitude}')}"
    elif address:
        map_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
    return " ".join(sentences), map_url


@dataclass(frozen=True)
class TravelDocument:
    text: str
    source: str

    @property
    def title(self) -> str:
        match = re.search(r"(?:Hotel|Hotel name|Name|Campsite|Adventure|Getaway Ideas?):\s*(.+)", self.text)
        if match:
            title = _normalize_value(match.group(1).strip())
            if title.startswith("[") and title.endswith("]"):
                title = title[1:-1].strip()
            return title
        return self.source.replace("_", " ").title()


class KenyaTravelRAG:
    """Retrieves Kenya travel chunks from a persistent Chroma vector database."""

    def __init__(self, data_dir: Path, persist_dir: Path) -> None:
        from app.chroma_store import ChromaTravelStore
        self.store = ChromaTravelStore(data_dir, persist_dir)

    def answer(self, question: str) -> dict:
        matches = self.store.search(question)
        if not matches:
            return {
                "answer": "I could not find a close match in the Kenya travel knowledge base. Try naming a destination, hotel type, budget, or travel interest.",
                "sources": [],
            }
        results = []
        seen = set()
        for match in matches:
            metadata = match.get("metadata") or {}
            text = match.get("text") or ""
            if not text:
                continue
            document = TravelDocument(text, str(metadata.get("source", "Kenya travel data")))
            title = metadata.get("accommodation_name") or metadata.get("title") or document.title
            document = TravelDocument(f"Name: {title}\n{document.text}", document.source)
            key = (document.title, document.source)
            if key in seen:
                continue
            seen.add(key)
            details, map_url = _natural_details(document, metadata)
            context = _travel_facts(document.text, metadata)
            results.append({"title": document.title, "excerpt": details, "map_url": map_url, "raw_context": f"Travel facts:\n{context}"})

        lead = "I found these relevant options in the Kenya travel data:"
        if any(word in question.lower() for word in ("plan", "itinerary", "trip")):
            lead = "For this trip, use the following retrieved Kenya options as the building blocks for your itinerary:"
        return {"answer": lead, "sources": results[:4]}
