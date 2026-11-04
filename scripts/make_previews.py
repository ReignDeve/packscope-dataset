from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "images"
LABELS = ROOT / "labels"
CLASSES = ROOT / "classes.txt"
OUT = ROOT / "previews"
MAX_SIDE = 1200
COLOR = (255, 40, 40)


def load_font(size: int):
    for name in ("arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    classes = [l.strip() for l in CLASSES.read_text(encoding="utf-8").splitlines() if l.strip()]
    OUT.mkdir(exist_ok=True)
    font = load_font(32)
    count = 0
    for img_path in sorted(IMAGES.glob("*.jpg")):
        label_path = LABELS / f"{img_path.stem}.txt"
        if not label_path.exists():
            print(f"skip {img_path.name}: no label file")
            continue
        with Image.open(img_path) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")  # no-op if orientation is already 1
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        W, H = im.size
        draw = ImageDraw.Draw(im)
        line_w = max(3, round(max(W, H) / 300))
        for line in label_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            cid, x, y, w, h = line.split()
            cid = int(cid)
            x, y, w, h = float(x) * W, float(y) * H, float(w) * W, float(h) * H
            box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            draw.rectangle(box, outline=COLOR, width=line_w)
            name = classes[cid] if 0 <= cid < len(classes) else "?"
            text = f"{cid} {name}"
            tb = draw.textbbox((0, 0), text, font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            tx = max(0, min(box[0], W - tw - 12))
            ty = box[1] - th - 12 if box[1] - th - 12 >= 0 else box[1]
            draw.rectangle((tx, ty, tx + tw + 12, ty + th + 12), fill=COLOR)
            draw.text((tx + 6 - tb[0], ty + 6 - tb[1]), text, fill=(255, 255, 255), font=font)
        im.save(OUT / f"{img_path.stem}_annotated.jpg", "JPEG", quality=90)
        count += 1
    print(f"Wrote {count} previews to {OUT}")


if __name__ == "__main__":
    main()
