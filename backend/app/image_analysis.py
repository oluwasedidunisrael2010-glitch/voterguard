"""Basic, transparent image checks. These are review signals, not proof of anything."""
import hashlib
import io

import cv2
import imagehash
import numpy as np
from PIL import Image

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_PIXELS = 40_000_000
MIN_SIDE_WARN = 300
BLUR_WARN_BELOW = 100.0
DARK_WARN_BELOW = 40.0
BRIGHT_WARN_ABOVE = 215.0
LOW_CONTRAST_BELOW = 25.0

EXIF_TAGS = {271: "Make", 272: "Model", 305: "Software", 306: "DateTime"}

LIMITATIONS = [
    "Metadata checks do not prove a photo is genuine or fake; metadata is often stripped or edited.",
    "This tool cannot prove an image is AI-generated.",
    "Perceptual-hash similarity is a visual-similarity signal, not facial recognition or identity proof.",
    "Matching only covers the locally loaded reference collection, not any national register.",
    "Every flag requires human review before any action is taken.",
]


class ImageRejected(ValueError):
    """Raised when an upload is not a safe, readable image."""


def phash_distance(a_hex: str, b_hex: str) -> int:
    return int(imagehash.hex_to_hash(a_hex) - imagehash.hex_to_hash(b_hex))


def analyze_image_bytes(data: bytes) -> dict:
    if not data:
        raise ImageRejected("The file is empty.")

    sha256 = hashlib.sha256(data).hexdigest()

    # Pass 1: cheap header checks before any full decode.
    try:
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
            width, height = probe.size
            if fmt not in ALLOWED_FORMATS:
                raise ImageRejected(
                    f"Unsupported image format '{fmt}'. Allowed: JPEG, PNG, WEBP."
                )
            if width * height > MAX_PIXELS:
                raise ImageRejected("Image dimensions are too large to process safely.")
            probe.verify()
    except ImageRejected:
        raise
    except Exception:
        raise ImageRejected("The file is not a readable image.")

    # Pass 2: full decode with Pillow (metadata + hash) and OpenCV (quality metrics).
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        exif = img.getexif()
        rgb = img.convert("RGB")
        phash = str(imagehash.phash(rgb))
    except Exception:
        raise ImageRejected("The image is corrupted or could not be decoded.")

    bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ImageRejected("The image could not be decoded.")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    contrast = float(gray.std())
    exif_fields = {name: str(exif.get(tag)) for tag, name in EXIF_TAGS.items() if tag in exif}
    has_exif = len(exif) > 0

    findings = []

    def add(check: str, status: str, detail: str) -> None:
        findings.append({"check": check, "status": status, "detail": detail})

    add("format", "pass", f"Readable {fmt} image, {width}x{height} pixels.")
    if min(width, height) < MIN_SIDE_WARN:
        add("resolution", "warn", f"Small image ({width}x{height}); may be too low quality for review.")
    else:
        add("resolution", "pass", "Resolution is adequate for review.")
    if blur_score < BLUR_WARN_BELOW:
        add("sharpness", "warn", f"Low sharpness score ({blur_score:.1f}); image may be blurred.")
    else:
        add("sharpness", "pass", f"Sharpness score {blur_score:.1f}.")
    if brightness < DARK_WARN_BELOW:
        add("brightness", "warn", f"Image is very dark (mean {brightness:.0f}/255).")
    elif brightness > BRIGHT_WARN_ABOVE:
        add("brightness", "warn", f"Image is very bright (mean {brightness:.0f}/255).")
    else:
        add("brightness", "pass", f"Brightness is within normal range (mean {brightness:.0f}/255).")
    if contrast < LOW_CONTRAST_BELOW:
        add("contrast", "warn", f"Low contrast ({contrast:.0f}); image may be washed out or blank.")
    else:
        add("contrast", "pass", f"Contrast is adequate ({contrast:.0f}).")
    if has_exif:
        add("metadata", "info", "Embedded metadata present. This does not prove the photo is genuine.")
    else:
        add("metadata", "info", "No embedded metadata. Common for screenshots or re-saved images; not proof of anything.")

    return {
        "sha256": sha256,
        "size_bytes": len(data),
        "image_format": fmt,
        "width": width,
        "height": height,
        "phash": phash,
        "metrics": {
            "blur_score": round(blur_score, 2),
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "has_exif": has_exif,
            "exif_fields": exif_fields,
        },
        "findings": findings,
        "warning_count": sum(1 for f in findings if f["status"] == "warn"),
        "limitations": LIMITATIONS,
    }
