#!/usr/bin/env python3
"""
Download and process Wikimedia Commons photos for The Pipeline scroll.
Each photo is cropped to 400x400 face-filling JPEG at quality 92.
"""

import os
import sys
import time
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_SIZE = 400
JPEG_QUALITY = 92

# User-Agent required by Wikimedia
HEADERS = {
    'User-Agent': 'DisclosureScrollsBot/1.0 (documentary research project; Python/urllib)'
}


def download_image(url):
    """Download image from URL, return PIL Image or None."""
    print(f"  Downloading: {url}")
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        img = Image.open(BytesIO(data))
        img = img.convert('RGB')
        print(f"  Downloaded: {img.size[0]}x{img.size[1]}")
        return img
    except Exception as e:
        print(f"  FAILED: {e}")
        return None


def face_crop_resize(img, face_bias_top=0.35):
    """
    Crop image to square (face-filling) then resize to TARGET_SIZE.
    face_bias_top: how far from the top the face center is (0.35 = upper third).
    For wider-than-tall images, center crop.
    For taller-than-wide images, crop from upper-center area.
    """
    w, h = img.size

    if w == h:
        # Already square
        pass
    elif w > h:
        # Wider than tall: center crop horizontally
        left = (w - h) // 2
        img = img.crop((left, 0, left + h, h))
    else:
        # Taller than wide: crop to square from upper portion
        # Place center of crop at face_bias_top fraction of height
        square_size = w
        center_y = int(h * face_bias_top)
        top = max(0, center_y - square_size // 2)
        # Make sure we don't go past bottom
        if top + square_size > h:
            top = h - square_size
        img = img.crop((0, top, square_size, top + square_size))

    # Resize to target
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)
    return img


def create_text_card(name, subtitle, filename):
    """Create a PIL text card as fallback."""
    img = Image.new('RGB', (TARGET_SIZE, TARGET_SIZE), color=(13, 17, 23))
    draw = ImageDraw.Draw(img)

    # Try to use a decent font
    font_name = None
    font_subtitle = None
    for font_path in [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
    ]:
        if os.path.exists(font_path):
            font_name = ImageFont.truetype(font_path, 28)
            font_subtitle = ImageFont.truetype(
                font_path.replace('Bold', 'Regular').replace('-Bold', ''),
                16
            )
            break

    if font_name is None:
        font_name = ImageFont.load_default()
        font_subtitle = font_name

    # Draw name centered
    bbox = draw.textbbox((0, 0), name, font=font_name)
    tw = bbox[2] - bbox[0]
    x = (TARGET_SIZE - tw) // 2
    draw.text((x, 160), name, fill='white', font=font_name)

    # Draw subtitle centered
    bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    tw = bbox[2] - bbox[0]
    x = (TARGET_SIZE - tw) // 2
    draw.text((x, 205), subtitle, fill=(0, 200, 80), font=font_subtitle)

    output_path = os.path.join(ASSETS_DIR, filename)
    img.save(output_path, 'JPEG', quality=JPEG_QUALITY)
    print(f"  Created text card: {filename}")


def process_person(filename, urls, name, subtitle, face_bias=0.35):
    """Try downloading from URLs in order, process and save."""
    print(f"\n{'='*60}")
    print(f"Processing: {name} -> {filename}")
    print(f"{'='*60}")

    for url in urls:
        img = download_image(url)
        if img is not None:
            # Check if image is large enough
            w, h = img.size
            min_dim = min(w, h)
            if min_dim < 100:
                print(f"  Image too small ({w}x{h}), trying next URL...")
                continue

            img = face_crop_resize(img, face_bias_top=face_bias)
            output_path = os.path.join(ASSETS_DIR, filename)
            img.save(output_path, 'JPEG', quality=JPEG_QUALITY)
            print(f"  Saved: {filename} ({TARGET_SIZE}x{TARGET_SIZE})")
            return True

    # All URLs failed - create text card
    print(f"  All URLs failed for {name}, creating text card fallback")
    create_text_card(name, subtitle, filename)
    return False


# ============================================================
# PEOPLE TO PROCESS
# ============================================================

people = [
    {
        'filename': 'gottlieb.jpg',
        'name': 'Sidney Gottlieb',
        'subtitle': 'CIA — MKUltra Director',
        'face_bias': 0.35,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/1/11/Sidney_Gottlieb_photo.jpg',
        ]
    },
    {
        'filename': 'kesey.jpg',
        'name': 'Ken Kesey',
        'subtitle': 'Author — Acid Tests',
        'face_bias': 0.33,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/a/aa/Ken_Kesey_%28One_Flew_Over_the_Cuckoo%27s_Nest_photo%29.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/4/46/Ken_Kesey_in_Pasadena_in_1974_from_The_Big_T_1974_%28page_45_crop%29.jpg',
        ]
    },
    {
        'filename': 'leary.jpg',
        'name': 'Timothy Leary',
        'subtitle': 'Harvard — LSD Advocate',
        'face_bias': 0.33,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/0/05/Timothy_Leary_%281969_press_photo%29.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/8/86/Dr._Timothy_Leary_%281970_AP_Photo%29.jpg',
        ]
    },
    {
        'filename': 'morrison_sr.jpg',
        'name': 'George S. Morrison',
        'subtitle': 'USN Rear Admiral',
        'face_bias': 0.30,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/3/35/Admiral_George_Stephen_Morrison.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/d/d4/George_S._Morrison%2C_Admiral.jpg',
        ]
    },
    {
        'filename': 'zappa.jpg',
        'name': 'Frank Zappa',
        'subtitle': 'Musician — Laurel Canyon',
        'face_bias': 0.32,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/2/22/Frank_Zappa_1973.JPG',
        ]
    },
    {
        'filename': 'bennewitz.jpg',
        'name': 'Paul Bennewitz',
        'subtitle': 'Physicist — AFOSI Target',
        'face_bias': 0.35,
        'urls': [
            # Paul Bennewitz has no known freely licensed photo
            # Will fall through to text card
        ]
    },
    {
        'filename': 'huxley.jpg',
        'name': 'Aldous Huxley',
        'subtitle': 'Author — Brave New World',
        'face_bias': 0.33,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/0/0a/Aldous_Huxley_1947.png',
            'https://upload.wikimedia.org/wikipedia/commons/e/e9/Aldous_Huxley_psychical_researcher.png',
            'https://upload.wikimedia.org/wikipedia/commons/9/91/Aldous_Huxley_-_photo_Henri_Manuel.jpg',
        ]
    },
    {
        'filename': 'blavatsky.jpg',
        'name': 'Helena Blavatsky',
        'subtitle': 'Theosophical Society Founder',
        'face_bias': 0.32,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/1/10/Mme._Blavatsky%2C_head-and-shoulders_portrait_LCCN2005688465.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/2/20/Helena_Blavatsky.jpg',
            'https://upload.wikimedia.org/wikipedia/commons/b/b8/H.P._Blavatsky.jpg',
        ]
    },
    {
        'filename': 'bailey.jpg',
        'name': 'Alice Bailey',
        'subtitle': 'Lucis Trust Founder',
        'face_bias': 0.30,
        'urls': [
            'https://upload.wikimedia.org/wikipedia/commons/e/ed/Alice_Bailey_in_1940s.jpg',
        ]
    },
]


def main():
    print("=" * 60)
    print("DISCLOSURE SCROLLS — Photo Downloader")
    print(f"Target: {ASSETS_DIR}")
    print(f"Size: {TARGET_SIZE}x{TARGET_SIZE} JPEG Q{JPEG_QUALITY}")
    print("=" * 60)

    results = {'success': [], 'fallback': [], 'failed': []}

    for person in people:
        ok = process_person(
            person['filename'],
            person['urls'],
            person['name'],
            person['subtitle'],
            person.get('face_bias', 0.35)
        )
        if ok:
            results['success'].append(person['name'])
        else:
            results['fallback'].append(person['name'])

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Real photos: {len(results['success'])}")
    for name in results['success']:
        print(f"  [OK] {name}")
    print(f"Text card fallbacks: {len(results['fallback'])}")
    for name in results['fallback']:
        print(f"  [FALLBACK] {name}")


if __name__ == '__main__':
    main()
