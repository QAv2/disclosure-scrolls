#!/usr/bin/env python3
"""
Generate steganographic seed images for each Disclosure Scroll.
Each image contains the complete scroll + shared assets as a self-contained archive.

Usage: python3 generate_seeds.py [--scroll NAME] [--full-only]

Requires: steg.py at ~/Desktop/steg.py
"""

import os
import shutil
import sys
import tempfile

# Add steg.py location to path
STEG_PATH = os.path.expanduser("~/Desktop/steg.py")
sys.path.insert(0, os.path.dirname(STEG_PATH))

from steg import (
    generate_carrier_image, embed_payload, tar_directory,
    capacity, DEFAULT_EXCLUDES,
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

SCROLLS = {
    "ai-wars":       {"style": "nebula",   "size": (2560, 1440)},
    "money-wars":    {"style": "terrain",  "size": (1920, 1080)},
    "space-wars":    {"style": "nightsky", "size": (3200, 1800)},
    "mind-wars":     {"style": "nebula",   "size": (1920, 1080)},
    "oil-wars":      {"style": "terrain",  "size": (2560, 1440)},
    "media-wars":    {"style": "gradient", "size": (2560, 1440)},
    "body-wars":     {"style": "gradient", "size": (2560, 1440)},
    "sky-wars":      {"style": "nightsky", "size": (1920, 1080)},
    "faith-wars":    {"style": "nebula",   "size": (1920, 1080)},
    "the-pipeline":  {"style": "gradient", "size": (1920, 1080)},
    "the-web":       {"style": "terrain",  "size": (3200, 1800)},
}

EXCLUDES = DEFAULT_EXCLUDES | {"seed.png", "seed-full.png", "og-image.png",
                                "generate_seeds.py", "seed-readme.txt",
                                ".gitignore"}

LSB_DEPTH = 2
COMPRESS = "zlib"


def build_scroll_package(scroll_name, tmp_dir):
    """Build a self-contained scroll package in tmp_dir."""
    scroll_src = os.path.join(PROJECT_ROOT, scroll_name)
    if not os.path.isdir(scroll_src):
        print(f"  SKIP: {scroll_name} not found")
        return None

    # Copy scroll directory (excluding seed.png)
    scroll_dst = os.path.join(tmp_dir, scroll_name)
    shutil.copytree(scroll_src, scroll_dst,
                    ignore=shutil.ignore_patterns("seed.png", "og-image.png"))

    # Copy shared CSS/JS from ai-wars (if this isn't ai-wars itself)
    shared_css_src = os.path.join(PROJECT_ROOT, "ai-wars", "css")
    shared_js_src = os.path.join(PROJECT_ROOT, "ai-wars", "js")
    shared_dst = os.path.join(tmp_dir, "ai-wars")

    if scroll_name != "ai-wars":
        os.makedirs(os.path.join(shared_dst, "css"), exist_ok=True)
        os.makedirs(os.path.join(shared_dst, "js"), exist_ok=True)
        for f in os.listdir(shared_css_src):
            shutil.copy2(os.path.join(shared_css_src, f),
                         os.path.join(shared_dst, "css", f))
        for f in os.listdir(shared_js_src):
            shutil.copy2(os.path.join(shared_js_src, f),
                         os.path.join(shared_dst, "js", f))

    # Copy extract.py and README
    shutil.copy2(os.path.join(PROJECT_ROOT, "extract.py"),
                 os.path.join(tmp_dir, "extract.py"))
    shutil.copy2(os.path.join(PROJECT_ROOT, "seed-readme.txt"),
                 os.path.join(tmp_dir, "README.txt"))

    # Create redirect index.html
    with open(os.path.join(tmp_dir, "index.html"), "w") as f:
        f.write(f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0;url={scroll_name}/">
<title>Redirecting...</title>
</head><body>
<p>Opening <a href="{scroll_name}/">{scroll_name}</a>...</p>
</body></html>
""")

    return tmp_dir


def _rewrite_paths_for_local(tmp_dir):
    """Rewrite absolute paths in HTML to relative so the archive works as local files."""
    import re
    # Root index.html: /ai-wars/ → ai-wars/, /favicon.svg → favicon.svg
    root_html = os.path.join(tmp_dir, "index.html")
    if os.path.exists(root_html):
        with open(root_html, "r") as f:
            content = f.read()
        content = re.sub(r'(href|src)="/', r'\1="', content)
        with open(root_html, "w") as f:
            f.write(content)

    # Scroll index.html files: /ai-wars/ → ../ai-wars/, / → ../
    for name in SCROLLS:
        scroll_html = os.path.join(tmp_dir, name, "index.html")
        if not os.path.exists(scroll_html):
            continue
        with open(scroll_html, "r") as f:
            content = f.read()
        # Replace absolute paths with relative parent paths
        # href="/" → href="../" (back to root)
        content = re.sub(r'(href|src)="/([^"]+)"', r'\1="../\2"', content)
        content = re.sub(r'(href|src)="/"', r'\1="../"', content)
        with open(scroll_html, "w") as f:
            f.write(content)


def build_full_site_package(tmp_dir):
    """Build a package with all scrolls + index."""
    # Copy root index.html
    shutil.copy2(os.path.join(PROJECT_ROOT, "index.html"),
                 os.path.join(tmp_dir, "index.html"))

    # Copy each scroll
    for name in SCROLLS:
        scroll_src = os.path.join(PROJECT_ROOT, name)
        if os.path.isdir(scroll_src):
            scroll_dst = os.path.join(tmp_dir, name)
            shutil.copytree(scroll_src, scroll_dst,
                            ignore=shutil.ignore_patterns("seed.png", "og-image.png"))

    # Copy shared assets
    for item in ["favicon.svg", "favicon.png", "apple-touch-icon.png", "robots.txt"]:
        src = os.path.join(PROJECT_ROOT, item)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(tmp_dir, item))

    # Copy extract.py and README
    shutil.copy2(os.path.join(PROJECT_ROOT, "extract.py"),
                 os.path.join(tmp_dir, "extract.py"))
    shutil.copy2(os.path.join(PROJECT_ROOT, "seed-readme.txt"),
                 os.path.join(tmp_dir, "README.txt"))

    # Rewrite absolute paths to relative so the archive works as local files
    _rewrite_paths_for_local(tmp_dir)

    return tmp_dir


def generate_scroll_seed(scroll_name, config):
    """Generate seed image for a single scroll."""
    print(f"\n{'='*60}")
    print(f"Generating seed: {scroll_name}")
    print(f"{'='*60}")

    width, height = config["size"]
    style = config["style"]
    output_path = os.path.join(PROJECT_ROOT, scroll_name, "assets", "seed.png")

    # Ensure assets dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Build package
        pkg_dir = os.path.join(tmp_dir, "package")
        os.makedirs(pkg_dir)
        result = build_scroll_package(scroll_name, pkg_dir)
        if not result:
            return False

        # Tar the package
        payload = tar_directory(pkg_dir, EXCLUDES)
        print(f"  Payload: {len(payload):,} bytes")

        # Check capacity
        cap = capacity(width, height, LSB_DEPTH)
        import zlib
        compressed_est = len(zlib.compress(payload, 9))
        print(f"  Compressed est: {compressed_est:,} bytes")
        print(f"  Carrier capacity: {cap:,} bytes ({width}x{height})")

        if compressed_est > cap:
            print(f"  WARNING: May not fit! Trying larger carrier...")
            width = int(width * 1.5)
            height = int(height * 1.5)
            cap = capacity(width, height, LSB_DEPTH)
            print(f"  Upgraded to {width}x{height} ({cap:,} bytes)")

        # Generate carrier
        carrier_path = os.path.join(tmp_dir, "carrier.png")
        import time
        generate_carrier_image(carrier_path, width, height, style,
                               seed=int(time.time() * 1000))

        # Embed
        result = embed_payload(carrier_path, payload, output_path,
                               LSB_DEPTH, COMPRESS, password=None,
                               flags=0x02)  # FLAG_DIRECTORY

        print(f"  Output: {output_path}")
        print(f"  Compressed: {result['compressed_size']:,} bytes")
        print(f"  Used: {result['used_pct']:.1f}%")

    return True


def generate_full_site_seed():
    """Generate the full-site seed image for the index page."""
    print(f"\n{'='*60}")
    print(f"Generating FULL SITE seed")
    print(f"{'='*60}")

    width, height = 6000, 4000
    output_path = os.path.join(PROJECT_ROOT, "seed-full.png")

    with tempfile.TemporaryDirectory() as tmp_dir:
        pkg_dir = os.path.join(tmp_dir, "package")
        os.makedirs(pkg_dir)
        build_full_site_package(pkg_dir)

        payload = tar_directory(pkg_dir, EXCLUDES)
        print(f"  Payload: {len(payload):,} bytes")

        cap = capacity(width, height, LSB_DEPTH)
        import zlib
        compressed_est = len(zlib.compress(payload, 9))
        print(f"  Compressed est: {compressed_est:,} bytes")
        print(f"  Carrier capacity: {cap:,} bytes")

        carrier_path = os.path.join(tmp_dir, "carrier.png")
        import time
        generate_carrier_image(carrier_path, width, height, "nebula",
                               seed=int(time.time() * 1000))

        result = embed_payload(carrier_path, payload, output_path,
                               LSB_DEPTH, COMPRESS, password=None,
                               flags=0x02)

        print(f"  Output: {output_path}")
        print(f"  Compressed: {result['compressed_size']:,} bytes")
        print(f"  Used: {result['used_pct']:.1f}%")

    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate seed images")
    parser.add_argument("--scroll", help="Generate for a specific scroll only")
    parser.add_argument("--full-only", action="store_true",
                        help="Only generate the full-site seed")
    args = parser.parse_args()

    if args.full_only:
        generate_full_site_seed()
    elif args.scroll:
        if args.scroll not in SCROLLS:
            print(f"Unknown scroll: {args.scroll}")
            print(f"Available: {', '.join(SCROLLS.keys())}")
            sys.exit(1)
        generate_scroll_seed(args.scroll, SCROLLS[args.scroll])
    else:
        # Generate all
        for name, config in SCROLLS.items():
            generate_scroll_seed(name, config)
        generate_full_site_seed()

    print("\nDone.")
