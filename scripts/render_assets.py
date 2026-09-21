#!/usr/bin/env python3
"""Render EchoDub web icons from the same waveform geometry as the iOS app."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"

INDIGO = (88, 91, 193, 255)
WHITE = (255, 255, 255, 255)
BG = (11, 12, 14, 255)
INK = (242, 243, 245, 255)
MUTED = (242, 243, 245, 148)
HEIGHTS = [0.26, 0.44, 0.72, 1.00, 0.58, 0.88, 0.40, 0.64, 0.30]


def rounded_rect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_waveform(draw, box, color):
    x0, y0, x1, y1 = box
    width = x1 - x0
    height = y1 - y0
    count = len(HEIGHTS)
    gap = width * 0.055
    bar_w = (width - gap * (count - 1)) / count
    cx = x0
    for h in HEIGHTS:
        bar_h = max(bar_w, height * h)
        left = cx
        top = y0 + (height - bar_h) / 2
        rounded_rect(
            draw,
            (left, top, left + bar_w, top + bar_h),
            radius=bar_w / 2,
            fill=color,
        )
        cx += bar_w + gap


def app_icon(size=1024, padding_ratio=196 / 1024):
    img = Image.new("RGBA", (size, size), INDIGO)
    draw = ImageDraw.Draw(img)
    pad = size * padding_ratio
    draw_waveform(draw, (pad, pad, size - pad, size - pad), WHITE)
    return img


def save_png(img, name):
    path = ASSETS / name
    img.save(path, "PNG")
    print(f"wrote {path}")


def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def og_image():
    w, h = 1200, 630
    img = Image.new("RGBA", (w, h), BG)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse((-180, -220, 620, 580), fill=(88, 91, 193, 70))
    draw.ellipse((720, 80, 1380, 760), fill=(88, 91, 193, 36))
    img = Image.alpha_composite(img, overlay.filter(ImageFilter.GaussianBlur(80)))
    draw = ImageDraw.Draw(img)

    icon = app_icon(220)
    mask = Image.new("L", (220, 220), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 219, 219), radius=52, fill=255)
    icon.putalpha(mask)
    img.alpha_composite(icon, (96, 205))

    title = load_font(72, bold=True)
    lede = load_font(32, bold=False)
    draw.text((360, 228), "EchoDub", font=title, fill=INK)
    draw.text((360, 322), "English voiceover. In your voice.", font=lede, fill=MUTED)
    return img.convert("RGB")


def main():
    ASSETS.mkdir(exist_ok=True)
    icon = app_icon(1024)
    save_png(icon, "icon.png")
    save_png(icon.resize((180, 180), Image.Resampling.LANCZOS), "apple-touch-icon.png")
    save_png(icon.resize((128, 128), Image.Resampling.LANCZOS), "favicon-128.png")
    save_png(icon.resize((32, 32), Image.Resampling.LANCZOS), "favicon-32.png")
    og_image().save(ASSETS / "og.png", "PNG")
    print(f"wrote {ASSETS / 'og.png'}")


if __name__ == "__main__":
    main()
