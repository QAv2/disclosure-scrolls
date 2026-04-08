#!/usr/bin/env python3
"""Cross-link Disclosure Scrolls entities to Intel Console dossiers."""

import json
import os
import re
import html
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

IC_BASE = "https://qav2.github.io/intel-console/#entity/"
ENTITIES_JSON = os.path.expanduser("~/intel-console/static/data/entities.json")

# Manual overrides for near-matches (scroll text -> IC entity ID)
MANUAL_OVERRIDES = {
    "bilderberg": 672,        # Bilderberg Group
    "skull & bones": 332,     # Skull and Bones
    "boeing": 598,            # Boeing Defense
}

SCROLLS = [
    "ai-wars", "body-wars", "faith-wars", "media-wars", "mind-wars",
    "money-wars", "oil-wars", "sky-wars", "space-wars", "the-pipeline", "the-web"
]

# CSS injected into each scroll
IC_LINK_CSS = """
/* ── Intel Console Cross-Links ───────────────────────────── */
a.ic-link {
  color: inherit;
  text-decoration: none;
  cursor: pointer;
  position: relative;
}
a.ic-link .company-badge {
  cursor: pointer;
  transition: filter 0.2s ease, box-shadow 0.2s ease;
}
a.ic-link:hover .company-badge,
a.ic-link:focus .company-badge {
  filter: brightness(1.3);
  box-shadow: 0 0 8px rgba(52, 211, 153, 0.2);
}
a.ic-link.ic-vr {
  border-bottom: 1px dotted rgba(52, 211, 153, 0.3);
  transition: border-color 0.2s ease, color 0.2s ease;
}
a.ic-link.ic-vr:hover,
a.ic-link.ic-vr:focus {
  border-color: rgba(52, 211, 153, 0.7);
  color: #34d399;
}
"""


def load_entity_mapping():
    """Build name -> (id, canonical_name) mapping from Intel Console entities."""
    with open(ENTITIES_JSON) as f:
        data = json.load(f)

    mapping = {}  # lowercase name -> (id, canonical_name)
    id_to_name = {}
    for eid, ent in data.items():
        name = ent["name"].strip()
        eid_int = int(eid)
        id_to_name[eid_int] = name
        mapping[name.lower()] = (eid_int, name)
        if ent.get("aliases"):
            for alias in ent["aliases"].split(","):
                alias = alias.strip()
                if alias:
                    mapping[alias.lower()] = (eid_int, name)

    # Apply manual overrides
    for text, eid in MANUAL_OVERRIDES.items():
        canonical = id_to_name.get(eid, text)
        mapping[text.lower()] = (eid, canonical)

    return mapping


def process_scroll(scroll_dir, mapping, dry_run=False):
    """Process a single scroll HTML file and add Intel Console links."""
    html_path = scroll_dir / "index.html"
    if not html_path.exists():
        return {"scroll": scroll_dir.name, "badges": 0, "vr_names": 0, "unmatched": []}

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")
    stats = {"scroll": scroll_dir.name, "badges": 0, "vr_names": 0, "matched": [], "unmatched": []}

    # --- 1. Link company-badge spans ---
    for badge in soup.find_all("span", class_="company-badge"):
        # Skip if already wrapped in a link
        if badge.parent and badge.parent.name == "a":
            continue

        badge_text = badge.get_text(strip=True)
        # Decode HTML entities for matching
        decoded = html.unescape(badge_text)
        lookup = decoded.lower()

        if lookup in mapping:
            eid, canonical = mapping[lookup]
            link = soup.new_tag(
                "a",
                href=f"{IC_BASE}{eid}",
                target="_blank",
                rel="noopener",
                title=f"View {canonical} in Intel Console",
            )
            link["class"] = ["ic-link"]
            badge.wrap(link)
            stats["badges"] += 1
            stats["matched"].append((decoded, eid, "badge"))
        else:
            stats["unmatched"].append((decoded, "badge"))

    # --- 2. Link vr-name divs ---
    for vr in soup.find_all("div", class_="vr-name"):
        # Skip if already contains a link
        if vr.find("a"):
            continue

        vr_text = vr.get_text(strip=True)
        decoded = html.unescape(vr_text)
        lookup = decoded.lower()

        if lookup in mapping:
            eid, canonical = mapping[lookup]
            link = soup.new_tag(
                "a",
                href=f"{IC_BASE}{eid}",
                target="_blank",
                rel="noopener",
                title=f"View {canonical} in Intel Console",
            )
            link["class"] = ["ic-link", "ic-vr"]
            # Move vr-name's content into the link
            for child in list(vr.children):
                child.extract()
                link.append(child)
            vr.append(link)
            stats["vr_names"] += 1
            stats["matched"].append((decoded, eid, "vr-name"))
        else:
            stats["unmatched"].append((decoded, "vr-name"))

    # --- 3. Inject CSS if any links were added ---
    if stats["badges"] + stats["vr_names"] > 0:
        head = soup.find("head")
        if head:
            # Check if CSS already injected
            existing = head.find("style", string=re.compile("Intel Console Cross-Links"))
            if not existing:
                style_tag = soup.new_tag("style")
                style_tag.string = IC_LINK_CSS
                head.append(style_tag)

    # --- 4. Save ---
    if not dry_run and stats["badges"] + stats["vr_names"] > 0:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

    return stats


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Cross-link Disclosure Scrolls → Intel Console")
    parser.add_argument("--dry-run", action="store_true", help="Don't write files, just report matches")
    args = parser.parse_args()

    mapping = load_entity_mapping()
    print(f"Loaded {len(mapping)} entity name/alias entries\n")

    base = Path(__file__).parent
    total_badges = 0
    total_vr = 0
    all_unmatched = []

    for scroll_name in SCROLLS:
        scroll_dir = base / scroll_name
        stats = process_scroll(scroll_dir, mapping, dry_run=args.dry_run)
        linked = stats["badges"] + stats["vr_names"]
        total_badges += stats["badges"]
        total_vr += stats["vr_names"]

        if linked > 0:
            print(f"  {scroll_name}: {stats['badges']} badges, {stats['vr_names']} vr-names linked")
            for name, eid, kind in stats["matched"]:
                print(f"    ✓ {name} → #{eid} ({kind})")
        else:
            print(f"  {scroll_name}: no matches")

        if stats["unmatched"]:
            all_unmatched.extend([(scroll_name, n, k) for n, k in stats["unmatched"]])

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}TOTAL: {total_badges} badges + {total_vr} vr-names = {total_badges + total_vr} links")

    if all_unmatched:
        # Deduplicate
        seen = set()
        unique = []
        for scroll, name, kind in all_unmatched:
            if name not in seen:
                seen.add(name)
                unique.append((scroll, name, kind))
        print(f"\nUnmatched entities ({len(unique)} unique):")
        for scroll, name, kind in sorted(unique, key=lambda x: x[1]):
            print(f"  ✗ {name} ({kind}) — first seen in {scroll}")


if __name__ == "__main__":
    main()
