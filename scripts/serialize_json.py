"""Serialize/flatten nested JSON records into embedding-ready text chunks.

Usage examples:
  python scripts/serialize_json.py \
    --input data/clean_data/kenyan_hotels.json \
    --output out/chunks.jsonl \
    --format jsonl

Outputs either a plain text file with chunks separated by a delimiter, or a JSONL
file where each line is a JSON object: {"text": ..., "metadata": {...}}
"""
from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Tuple


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
        # Represent simple values as key: value
        lines.append(f"{prefix}: {obj}")
    return lines


def record_chunks(record: Dict[str, Any], source: str = "", rec_index: int = 0) -> List[Tuple[str, Dict[str, Any]]]:
    """Turn a single top-level record into one or more (text, metadata) chunks.

    Strategy:
    - Build a header with top-level identifying fields (name, metadata.*, lat/lon)
    - For lists like `accommodations`, emit one chunk per item (keeping header)
    - If no accommodations, emit a single chunk with flattened fields
    """
    header_lines: List[str] = []
    meta = record.get("metadata", {}) if isinstance(record.get("metadata"), dict) else {}

    name = record.get("name") or meta.get("name")
    if name:
        header_lines.append(f"Name: {name}")

    # include some common top-level fields
    lat = record.get("latitude")
    lon = record.get("longitude")
    if lat is not None and lon is not None:
        header_lines.append(f"Location: {lat}, {lon}")

    # include flattened metadata
    header_lines.extend(flatten_json(meta, prefix="metadata"))

    chunks: List[Tuple[str, Dict[str, Any]]] = []

    # If record contains accommodations data, split it into meaningful chunks
    accommodations_key = None
    for key in ("accommodations", "accomodations"):
        if key in record:
            accommodations_key = key
            break

    if accommodations_key is not None:
        accommodations_value = record[accommodations_key]
        if isinstance(accommodations_value, list) and accommodations_value:
            for idx, acc in enumerate(accommodations_value, start=1):
                lines = header_lines.copy()
                lines.append("Accommodation:")
                lines.extend(flatten_json(acc, prefix="accommodation"))
                text = "\n".join(lines)
                metadata = {
                    "source": os.path.basename(source) if source else None,
                    "record_index": rec_index,
                    "chunk_type": "accommodation",
                    "accommodation_index": idx,
                    "hotel": name,
                }
                chunks.append((text, metadata))
        elif isinstance(accommodations_value, dict) and accommodations_value:
            for idx, (acc_name, acc_value) in enumerate(accommodations_value.items(), start=1):
                lines = header_lines.copy()
                lines.append("Accommodation:")
                lines.append(f"accommodation.name: {acc_name}")
                lines.append(f"accommodation.url: {acc_value}")
                text = "\n".join(lines)
                metadata = {
                    "source": os.path.basename(source) if source else None,
                    "record_index": rec_index,
                    "chunk_type": "accommodation",
                    "accommodation_index": idx,
                    "accommodation_name": acc_name,
                    "hotel": name,
                }
                chunks.append((text, metadata))
        else:
            # accommodations key exists but is empty or unsupported; emit a full record chunk
            lines = header_lines.copy()
            rest = {k: v for k, v in record.items() if k != "metadata"}
            lines.extend(flatten_json(rest, prefix="record"))
            text = "\n".join(lines)
            metadata = {
                "source": os.path.basename(source) if source else None,
                "record_index": rec_index,
                "chunk_type": "record",
                "hotel": name,
            }
            chunks.append((text, metadata))
    else:
        # generic full-record chunk
        lines = header_lines.copy()
        # flatten the rest of the record (excluding metadata) to capture other fields
        rest = {k: v for k, v in record.items() if k != "metadata"}
        lines.extend(flatten_json(rest, prefix="record"))
        text = "\n".join(lines)
        metadata = {
            "source": os.path.basename(source) if source else None,
            "record_index": rec_index,
            "chunk_type": "record",
            "hotel": name,
        }
        chunks.append((text, metadata))

    return chunks


def build_chunks_from_file(path: str) -> List[Tuple[str, Dict[str, Any]]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_chunks: List[Tuple[str, Dict[str, Any]]] = []
    if isinstance(data, list):
        for i, rec in enumerate(data):
            all_chunks.extend(record_chunks(rec, source=path, rec_index=i))
    elif isinstance(data, dict):
        # single top-level object: produce chunks for it
        all_chunks.extend(record_chunks(data, source=path, rec_index=0))
    else:
        raise ValueError("Unsupported JSON top-level type: must be list or dict")

    return all_chunks


def write_txt(chunks: List[Tuple[str, Dict[str, Any]]], out_path: str) -> None:
    sep = "\n\n---\n\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(sep.join(text for text, _ in chunks))


def write_jsonl(chunks: List[Tuple[str, Dict[str, Any]]], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        for text, metadata in chunks:
            obj = {"text": text, "metadata": metadata}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Flatten JSON into text chunks for RAG ingestion")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file path")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--format", "-f", choices=("txt", "jsonl"), default="jsonl")

    args = parser.parse_args()

    chunks = build_chunks_from_file(args.input)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    if args.format == "txt":
        write_txt(chunks, args.output)
    else:
        write_jsonl(chunks, args.output)

    print(f"Wrote {len(chunks)} chunks to {args.output}")


if __name__ == "__main__":
    main()
