#!/usr/bin/env python3
"""
Extract files hidden in a CNTYSEED steganographic image.
Only requires: pip install Pillow
Usage: python3 extract.py <image.png> <output_dir>
"""
import hashlib, io, os, struct, sys, tarfile, zlib
from PIL import Image

MAGIC = b"CNTYSEED"
HDR_SIZE = 64
HDR_FMT = "!8sBBBBII32sHH8s"


def lsb_decode(flat, depth, num_bytes):
    total_bits = num_bytes * 8
    pad = depth - (total_bits % depth) if total_bits % depth else 0
    slots = (total_bits + pad) // depth
    mask = (1 << depth) - 1
    bits = []
    for i in range(slots):
        val = flat[i] & mask
        for shift in range(depth - 1, -1, -1):
            bits.append((val >> shift) & 1)
    out = bytearray()
    for i in range(0, num_bytes * 8, 8):
        byte = 0
        for b in range(8):
            byte = (byte << 1) | bits[i + b]
        out.append(byte)
    return bytes(out)


def extract(image_path, output_dir):
    img = Image.open(image_path).convert("RGB")
    flat = [ch for px in img.getdata() for ch in px]

    # Probe LSB depths to find valid header
    hdr = None
    for depth in (1, 2, 3, 4):
        raw = lsb_decode(flat, depth, HDR_SIZE)
        if raw[:8] != MAGIC:
            continue
        fields = struct.unpack(HDR_FMT, raw)
        if fields[3] == depth:  # lsb_depth matches probe
            hdr = {
                "flags": fields[2], "lsb_depth": depth,
                "compression": fields[4], "original_size": fields[5],
                "compressed_size": fields[6], "sha256": fields[7],
            }
            break

    if not hdr:
        print("No embedded data found in this image.")
        sys.exit(1)

    if hdr["flags"] & 0x01:
        print("This image is encrypted. Use the full steg.py tool with a password.")
        sys.exit(1)

    print(f"Found: {hdr['original_size']:,} bytes, "
          f"{hdr['lsb_depth']}-LSB, "
          f"{'zlib' if hdr['compression'] == 1 else 'lzma' if hdr['compression'] == 2 else 'none'}")

    # Extract full payload
    total = HDR_SIZE + hdr["compressed_size"]
    raw = lsb_decode(flat, hdr["lsb_depth"], total)
    payload = raw[HDR_SIZE:]

    # Decompress
    if hdr["compression"] == 1:
        payload = zlib.decompress(payload)
    elif hdr["compression"] == 2:
        import lzma
        payload = lzma.decompress(payload)

    # Verify
    if hashlib.sha256(payload).digest() == hdr["sha256"]:
        print("Integrity: VERIFIED")
    else:
        print("WARNING: SHA-256 mismatch — data may be corrupted")

    # Extract
    os.makedirs(output_dir, exist_ok=True)
    if hdr["flags"] & 0x02:  # directory (tar)
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r") as tar:
            tar.extractall(path=output_dir, filter="data")
        print(f"Extracted to: {output_dir}/")
    else:
        out_file = os.path.join(output_dir, "extracted_data")
        with open(out_file, "wb") as f:
            f.write(payload)
        print(f"Written to: {out_file}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <image.png> <output_dir>")
        sys.exit(1)
    extract(sys.argv[1], sys.argv[2])
