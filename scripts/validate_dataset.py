import csv
import re
import sys
from collections import Counter
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
LABELS = ROOT / "labels"
METADATA = ROOT / "metadata.csv"
CLASSES = ROOT / "classes.txt"
DATA_YAML = ROOT / "data.yaml"

EXPECTED_COLUMNS = [
    "image_id", "brand", "product_name", "product_category", "product_subcategory",
    "material", "packaging_type", "net_quantity", "photographer", "annotator",
    "capture_date", "capture_setting", "device", "width", "height", "notes",
]
OPTIONAL_FIELDS = {"notes"}
CONTROLLED = {
    "product_category": {"preserved food", "dry goods", "dairy", "spread", "condiment",
                         "snack", "beverage", "meat product"},
    "material": {"metal", "glass", "plastic", "paper", "cardboard", "composite"},
    "packaging_type": {"can", "bag", "box", "jar", "carton", "bottle", "tub", "tube", "wrapper"},
    "capture_setting": {"handheld", "on_shelf", "on_surface"},
}
ORIENTATION_TAG = 0x0112
PLACEHOLDER_RE = re.compile(r"\[[^\]]*\]")

errors: list[str] = []
warnings: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load_classes() -> list[str]:
    classes = [l.strip() for l in CLASSES.read_text(encoding="utf-8").splitlines() if l.strip()]
    data = yaml.safe_load(DATA_YAML.read_text(encoding="utf-8"))
    names = data.get("names")
    if isinstance(names, dict):
        yaml_classes = [names[k] for k in sorted(names)]
        if sorted(names) != list(range(len(names))):
            error(f"data.yaml: names keys are not 0..{len(names) - 1}")
    else:
        yaml_classes = list(names or [])
    if classes != yaml_classes:
        error(f"classes.txt {classes} != data.yaml names {yaml_classes}")
    if set(classes) != CONTROLLED["packaging_type"] or len(classes) != len(set(classes)):
        error(f"classes.txt does not match the packaging_type vocabulary: {classes}")
    return classes


def read_label(path: Path, n_classes: int):
    """Return the class ID of the single box, or None if the file is invalid."""
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        warn(f"{path.name}: file does not end with a newline")
    lines = [l for l in raw.decode("utf-8").splitlines() if l.strip()]
    if len(lines) != 1:
        error(f"{path.name}: expected exactly 1 box, found {len(lines)}")
        if not lines:
            return None
    parts = lines[0].split()
    if len(parts) != 5:
        error(f"{path.name}: expected 5 values per line, got {len(parts)}")
        return None
    try:
        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:])
    except ValueError:
        error(f"{path.name}: non-numeric values: {lines[0]!r}")
        return None
    if not 0 <= cls < n_classes:
        error(f"{path.name}: class ID {cls} out of range 0..{n_classes - 1}")
    for name, v in (("x_center", x), ("y_center", y), ("width", w), ("height", h)):
        if not 0.0 <= v <= 1.0:
            error(f"{path.name}: {name}={v} outside [0, 1]")
    if w <= 0 or h <= 0:
        error(f"{path.name}: box has zero/negative size")
    eps = 1e-6
    if x - w / 2 < -eps or x + w / 2 > 1 + eps or y - h / 2 < -eps or y + h / 2 > 1 + eps:
        error(f"{path.name}: box extends beyond the image border")
    return cls


def main() -> int:
    classes = load_classes()

    # --- files ---------------------------------------------------------------
    image_files = sorted(p for p in IMAGES.iterdir() if p.is_file())
    for p in image_files:
        if p.suffix != ".jpg":
            error(f"images/{p.name}: extension must be lowercase .jpg")
    images = {p.stem: p for p in image_files}
    labels = {p.stem: p for p in sorted(LABELS.glob("*.txt"))}

    # --- metadata ------------------------------------------------------------
    raw = METADATA.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        error("metadata.csv: starts with a UTF-8 BOM")
    text = raw.decode("utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames != EXPECTED_COLUMNS:
        error(f"metadata.csv: unexpected columns {reader.fieldnames}")
    rows = {}
    for i, row in enumerate(reader, start=2):
        iid = row.get("image_id", "")
        if not iid.endswith(".jpg"):
            error(f"metadata.csv line {i}: image_id {iid!r} must end with .jpg")
        stem = Path(iid).stem
        if stem in rows:
            error(f"metadata.csv line {i}: duplicate image_id {iid}")
        rows[stem] = row
        for col in EXPECTED_COLUMNS:
            val = row.get(col)
            if val is None:
                continue
            if val != val.strip():
                warn(f"{iid}: {col} has leading/trailing whitespace ({val!r})")
            v = val.strip()
            if not v and col not in OPTIONAL_FIELDS:
                error(f"{iid}: {col} is empty (use 'unknown')")
            if v.lower() == "unknown":
                warn(f"{iid}: {col} is 'unknown'")
            if PLACEHOLDER_RE.search(v):
                warn(f"{iid}: {col} contains placeholder {v!r}")
        for col, allowed in CONTROLLED.items():
            v = (row.get(col) or "").strip()
            if v and v != "unknown" and v not in allowed:
                error(f"{iid}: {col}={v!r} not in controlled vocabulary")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", (row.get("capture_date") or "").strip()):
            if (row.get("capture_date") or "").strip() != "unknown":
                error(f"{iid}: capture_date {row.get('capture_date')!r} is not YYYY-MM-DD")

    # --- cross-reference -----------------------------------------------------
    for stem in sorted(set(images) | set(labels) | set(rows)):
        missing = [n for n, d in (("image", images), ("label", labels), ("metadata row", rows))
                   if stem not in d]
        if missing:
            error(f"{stem}: missing {', '.join(missing)}")

    # --- per-item checks -----------------------------------------------------
    class_counts: Counter = Counter()
    for stem in sorted(images):
        cls = read_label(labels[stem], len(classes)) if stem in labels else None
        if cls is not None and 0 <= cls < len(classes):
            class_counts[classes[cls]] += 1
        row = rows.get(stem)
        if row and cls is not None and 0 <= cls < len(classes):
            pt = row["packaging_type"].strip()
            if pt != classes[cls]:
                error(f"{stem}: packaging_type={pt!r} but label class {cls} = {classes[cls]!r}")
        if stem in images:
            with Image.open(images[stem]) as im:
                w, h = im.size
                orientation = im.getexif().get(ORIENTATION_TAG)
            if orientation not in (None, 1):
                error(f"{stem}: EXIF orientation is {orientation} (must be 1)")
            if row:
                try:
                    if int(row["width"]) != w or int(row["height"]) != h:
                        error(f"{stem}: metadata size {row['width']}x{row['height']} "
                              f"!= image size {w}x{h}")
                except ValueError:
                    error(f"{stem}: width/height not integer ({row['width']!r}, {row['height']!r})")
    for stem, p in labels.items():
        if stem not in images:
            read_label(p, len(classes))

    # --- report --------------------------------------------------------------
    print(f"Images: {len(images)}  Labels: {len(labels)}  Metadata rows: {len(rows)}")
    print("\nClass distribution:")
    for i, c in enumerate(classes):
        print(f"  {i} {c:<8} {class_counts.get(c, 0)}")
    print(f"  total      {sum(class_counts.values())}")

    print(f"\nWarnings ({len(warnings)}):")
    for w in warnings:
        print(f"  WARN  {w}")
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  ERROR {e}")
    print("\nResult:", "FAILED" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
