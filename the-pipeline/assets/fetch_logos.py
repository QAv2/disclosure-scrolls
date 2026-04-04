#!/usr/bin/env python3
"""
Fetch real organization logos/seals for The Pipeline scroll.
Public domain seals from Wikimedia Commons; PIL text cards for private orgs.
"""

import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = (13, 17, 23)  # #0d1117
SIZE = 400
LOGO_FIT = 300  # max logo dimension within canvas
QUALITY = 92

# User-Agent header required by Wikimedia
HEADERS = {
    "User-Agent": "DisclosureScrollsBot/1.0 (Documentary research project; PIL image processing)"
}

# ─── Download URLs (public domain / freely licensed) ─────────────────────────
DOWNLOADS = {
    "cia": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Seal_of_the_Central_Intelligence_Agency.svg/960px-Seal_of_the_Central_Intelligence_Agency.svg.png",
    "fbi": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Seal_of_the_FBI.svg/960px-Seal_of_the_FBI.svg.png",
    "afosi": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Air_Force_Office_of_Special_Investigations.png",
    "un": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Emblem_of_the_United_Nations.svg/960px-Emblem_of_the_United_Nations.svg.png",
    "sri": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/SRI_International_logo.svg/960px-SRI_International_logo.svg.png",
}

# ─── Text card definitions (private orgs without freely licensed logos) ───────
TEXT_CARDS = {
    "esalen": {
        "title": "ESALEN\nINSTITUTE",
        "subtitle": "Big Sur, California\nFounded 1962",
        "accent": (76, 175, 80),  # green
    },
    "lucis_trust": {
        "title": "LUCIS\nTRUST",
        "subtitle": "Est. 1922\nOriginally 'Lucifer Publishing'",
        "accent": (156, 120, 200),  # purple
    },
    "sandoz": {
        "title": "SANDOZ",
        "subtitle": "Laboratories\nBasel, Switzerland",
        "accent": (200, 80, 80),  # red
    },
    "tavistock": {
        "title": "TAVISTOCK\nINSTITUTE",
        "subtitle": "London, UK\nEst. 1947",
        "accent": (100, 160, 210),  # blue
    },
}


def download_image(url, dest_path):
    """Download an image from a URL with proper headers."""
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)
    print(f"  Downloaded: {os.path.basename(dest_path)} ({len(data):,} bytes)")
    return dest_path


def process_logo(input_path, output_path):
    """
    Open an image, scale to fit LOGO_FIT px, center on SIZE x SIZE dark canvas,
    save as JPEG.
    """
    img = Image.open(input_path).convert("RGBA")

    # Scale to fit within LOGO_FIT x LOGO_FIT
    w, h = img.size
    scale = min(LOGO_FIT / w, LOGO_FIT / h)
    new_w, new_h = int(w * scale), int(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Create dark background canvas
    canvas = Image.new("RGBA", (SIZE, SIZE), BG_COLOR + (255,))

    # Center the logo
    x = (SIZE - new_w) // 2
    y = (SIZE - new_h) // 2

    # Composite with alpha
    canvas.paste(img, (x, y), img)

    # Convert to RGB and save as JPEG
    final = canvas.convert("RGB")
    final.save(output_path, "JPEG", quality=QUALITY)
    print(f"  Processed:  {os.path.basename(output_path)} ({os.path.getsize(output_path):,} bytes)")


def make_text_card(name, config, output_path):
    """Create a styled text card for organizations without freely licensed logos."""
    canvas = Image.new("RGB", (SIZE, SIZE), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    title = config["title"]
    subtitle = config["subtitle"]
    accent = config["accent"]

    # Try to load a good font, fall back to default
    font_title = None
    font_sub = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    font_paths_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]

    for fp in font_paths:
        if os.path.exists(fp):
            font_title = ImageFont.truetype(fp, 36)
            break
    for fp in font_paths_regular:
        if os.path.exists(fp):
            font_sub = ImageFont.truetype(fp, 16)
            break

    if font_title is None:
        font_title = ImageFont.load_default()
    if font_sub is None:
        font_sub = ImageFont.load_default()

    # Draw decorative border
    border_color = accent
    # Outer border
    draw.rounded_rectangle(
        [(15, 15), (SIZE - 16, SIZE - 16)],
        radius=12,
        outline=border_color,
        width=2,
    )
    # Inner border (subtle)
    inner_color = tuple(c // 3 for c in accent)
    draw.rounded_rectangle(
        [(25, 25), (SIZE - 26, SIZE - 26)],
        radius=8,
        outline=inner_color,
        width=1,
    )

    # Decorative line above title
    draw.line([(80, 100), (SIZE - 80, 100)], fill=accent, width=2)

    # Draw title (centered, multiline)
    title_lines = title.split("\n")
    title_y = 120
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=font_title)
        tw = bbox[2] - bbox[0]
        tx = (SIZE - tw) // 2
        draw.text((tx, title_y), line, fill=(255, 255, 255), font=font_title)
        title_y += 46

    # Decorative line below title
    line_y = title_y + 15
    draw.line([(80, line_y), (SIZE - 80, line_y)], fill=accent, width=2)

    # Draw subtitle (centered, multiline)
    sub_lines = subtitle.split("\n")
    sub_y = line_y + 25
    for line in sub_lines:
        bbox = draw.textbbox((0, 0), line, font=font_sub)
        tw = bbox[2] - bbox[0]
        tx = (SIZE - tw) // 2
        draw.text((tx, sub_y), line, fill=accent, font=font_sub)
        sub_y += 24

    # Small decorative diamond at bottom
    cy = SIZE - 50
    cx = SIZE // 2
    diamond = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
    draw.polygon(diamond, fill=accent)

    canvas.save(output_path, "JPEG", quality=QUALITY)
    print(f"  Text card:  {os.path.basename(output_path)} ({os.path.getsize(output_path):,} bytes)")


def main():
    tmp_dir = os.path.join(ASSETS_DIR, "_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # ── Process downloadable logos ────────────────────────────────────────────
    print("=== Downloading and processing public domain seals ===\n")
    for name, url in DOWNLOADS.items():
        output_path = os.path.join(ASSETS_DIR, f"{name}.jpg")
        tmp_path = os.path.join(tmp_dir, f"{name}_raw.png")
        print(f"[{name.upper()}]")
        try:
            download_image(url, tmp_path)
            process_logo(tmp_path, output_path)
        except Exception as e:
            print(f"  ERROR: {e}")
        print()

    # ── Generate text cards for private orgs ──────────────────────────────────
    print("=== Generating text cards for private organizations ===\n")
    for name, config in TEXT_CARDS.items():
        output_path = os.path.join(ASSETS_DIR, f"{name}.jpg")
        print(f"[{name.upper()}]")
        try:
            make_text_card(name, config, output_path)
        except Exception as e:
            print(f"  ERROR: {e}")
        print()

    # ── Cleanup ───────────────────────────────────────────────────────────────
    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("=== Done! Temp files cleaned up. ===")


if __name__ == "__main__":
    main()
