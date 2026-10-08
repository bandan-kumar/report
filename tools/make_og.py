"""Generate the link-preview images (1200x630) and the home-screen icon.

Run by hand when the wording or the apps change: python3 tools/make_og.py
The PNG files are committed, so the deploy job does not need Pillow.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "og")
W, H = 1200, 630
NAVY_TOP, NAVY_BOTTOM = (14, 33, 64), (24, 48, 90)
ACCENT = (138, 184, 245)
WHITE = (255, 255, 255)
SOFT = (196, 212, 236)
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def background():
    img = Image.new("RGB", (W, H), NAVY_TOP)
    px = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        px.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(NAVY_TOP, NAVY_BOTTOM)))
    return img


def mark(img, x, y, size=64):
    """The BK mark used in the site header."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + size, y + size], radius=int(size * .3), fill=(59, 139, 232))
    f = font(BOLD, int(size * .42))
    d.text((x + size / 2, y + size / 2 + 2), "BK", font=f, fill=WHITE, anchor="mm")


def app_icon(slug, size):
    icon = Image.open(os.path.join(ROOT, "assets", "apps", f"{slug}.png")).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * .2237), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(icon, (0, 0), mask)
    return out


def wrap(d, text, f, max_w):
    lines, line = [], ""
    for word in text.split():
        trial = (line + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            line = trial
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def card(name, eyebrow, title, subtitle, icons=(), chips=(), icon_size=100, side=False):
    """side=True puts one large app icon on the right; otherwise icons run along the bottom."""
    img = background()
    d = ImageDraw.Draw(img)
    mark(img, 72, 64)
    d.text((152, 96), "Bandan Kumar", font=font(BOLD, 30), fill=WHITE, anchor="lm")
    text_w = 620 if side else W - 144
    d.text((72, 196), eyebrow.upper(), font=font(BOLD, 24), fill=ACCENT)
    f_title = font(BOLD, 68)
    y = 238
    for line in wrap(d, title, f_title, text_w):
        d.text((72, y), line, font=f_title, fill=WHITE)
        y += 78
    if subtitle:
        f_sub = font(REGULAR, 30)
        for line in wrap(d, subtitle, f_sub, text_w):
            d.text((72, y + 8), line, font=f_sub, fill=SOFT)
            y += 42
    text_end = y
    if side:
        size = 300
        icon = app_icon(icons[0], size)
        img.paste(icon, (W - 72 - size, (H - size) // 2 + 20), icon)
    else:
        top = H - 56 - icon_size
        assert text_end + 16 <= top, f"{name}: text ({text_end}) runs into the icon row ({top})"
        x = 72
        for slug in icons:
            icon = app_icon(slug, icon_size)
            img.paste(icon, (x, top), icon)
            x += icon_size + 20
        f_chip = font(BOLD, 24)
        x = W - 72
        for label in reversed(chips):
            w = d.textlength(label, font=f_chip) + 40
            cy = top + icon_size // 2
            d.rounded_rectangle([x - w, cy - 26, x, cy + 26], radius=26, fill=(30, 58, 104), outline=(70, 110, 170))
            d.text((x - w / 2, cy), label, font=f_chip, fill=WHITE, anchor="mm")
            x -= w + 12
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, name + ".png"), optimize=True)


APPS = [
    ("dietplan", "DietPlan", "Primary app", "iOS and Android"),
    ("upkee", "Upkee", "Primary app", "iOS, Android in development"),
    ("caloric", "Caloric", "Backup app", "iOS and Android"),
    ("locateus", "LocateUs", "Backup app", "iOS and Android"),
    ("keto", "Keto", "Backup app", "iOS and Android"),
]

if __name__ == "__main__":
    slugs = [a[0] for a in APPS]
    card("home", "Product Engineer", "Apps I build, ship and review.",
         "Two apps I own and three I back up, with live App Store data.", icons=slugs)
    card("q3-2026", "Performance review", "Q3 2026 Performance Review", "July to September 2026",
         icons=["dietplan", "caloric"], chips=["~7 weeks", "14 modules", "-77 MB app"])
    card("q4-2026", "Planning", "Q4 2026 Planning", "October to December 2026",
         icons=slugs, chips=["2 apps owned", "3 backed up"])
    for slug, name, role, platform in APPS:
        card(f"app-{slug}", role, name, platform, icons=[slug], side=True)
    # iOS home-screen icon
    icon = Image.new("RGB", (180, 180), (59, 139, 232))
    ImageDraw.Draw(icon).text((90, 92), "BK", font=font(BOLD, 78), fill=WHITE, anchor="mm")
    icon.save(os.path.join(ROOT, "assets", "icon-180.png"), optimize=True)
    print("generated", len(os.listdir(OUT)), "preview images")
