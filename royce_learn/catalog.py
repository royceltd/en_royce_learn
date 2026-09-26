"""Versioned, code-owned content; no executable HTML or remote fetches."""

import json
import re
from pathlib import Path

CONTENT = Path(__file__).parent / "content"


def load_catalog():
    catalog = json.loads((CONTENT / "catalog.json").read_text(encoding="utf-8"))
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog):
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported Learning content schema")
    ids = set()
    for guide in catalog["guides"]:
        key = guide["id"]
        if not re.fullmatch(r"[a-z][a-z0-9-]{1,79}", key) or key in ids:
            raise ValueError(f"Invalid or duplicate guide ID: {key}")
        ids.add(key)
        for field in ("title", "summary", "category", "version", "body"):
            if not guide.get(field):
                raise ValueError(f"Missing {field} on {key}")
        video = guide.get("video_id", "")
        if video and not re.fullmatch(r"[A-Za-z0-9_-]{11}", video):
            raise ValueError(f"Invalid YouTube video ID on {key}")
        if guide.get("permission", "read") not in ("read", "create", "write"):
            raise ValueError(f"Unsupported guide permission on {key}")
    for path in catalog["paths"]:
        if any(key not in ids for key in path["guides"]):
            raise ValueError(f"Unknown guide in learning path {path['id']}")


def permitted(guide, installed_apps, has_permission):
    return all(app in installed_apps for app in guide.get("required_apps", [])) and (
        not guide.get("doctype") or has_permission(guide["doctype"], guide.get("permission", "read"))
    )


def search_guides(guides, query="", category="", doctype=""):
    words = query.casefold().split()
    result = []
    for guide in guides:
        haystack = " ".join(
            [guide["title"], guide["summary"], guide["body"], " ".join(guide.get("keywords", []))]
        ).casefold()
        if category and guide["category"] != category:
            continue
        if doctype and guide.get("doctype") != doctype:
            continue
        if all(word in haystack for word in words):
            result.append(guide)
    return result
