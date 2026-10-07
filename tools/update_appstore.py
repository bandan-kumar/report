"""Refresh data/appstore.json from the public App Store lookup API (no key needed)."""
import json, os, re, struct, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = {
    "dietplan": 719586528,
    "upkee": 6757587275,
    "caloric": 6499521146,
    "locateus": 6739027332,
    "keto": 1475764462,
}
COUNTRY = "us"
PLAY_IDS = {
    "dietplan": "com.pixsterstudio.dietplans",
    "caloric": "com.pixsterstudio.caloric",
    "locateus": "com.pixsterstudio.locationtracker",
    "keto": "com.diet.pixsterstudio.ketodietican",
}


def fetch(app_id):
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={COUNTRY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["results"][0]


def ios_screenshots(r):
    """iPhone screenshots from the lookup result, resized for the web."""
    return [re.sub(r"/[^/]+$", "/392x696bb.jpg", u) for u in r.get("screenshotUrls", [])]


def image_size(data):
    """(width, height) of a PNG or JPEG, read from its header; None if unknown."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        i = 2
        while i + 9 < len(data):
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def is_phone_shot(url):
    """Google Play lists phone and tablet screenshots together; keep the tall phone ones."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        size = image_size(resp.read())
    return bool(size) and size[1] / size[0] >= 1.6


def play_screenshots(package):
    """Screenshot URLs from the public Google Play page. Returns [] if the page layout changes."""
    url = f"https://play.google.com/store/apps/details?id={package}&hl=en&gl={COUNTRY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", "replace")
    seen, out = set(), []
    for tag in re.findall(r'<img[^>]+alt="Screenshot image"[^>]*>', page):
        m = re.search(r'(?:src|data-src)="(https://play-lh\.googleusercontent\.com/[^"=]+)=', tag)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            shot = m.group(1) + "=w360-h640"
            if is_phone_shot(shot):
                out.append(shot)
    return out


def main():
    try:
        with open(os.path.join(ROOT, "data", "appstore.json")) as f:
            previous = json.load(f).get("apps", {})
    except (OSError, ValueError):
        previous = {}
    apps = {}
    for slug, app_id in IDS.items():
        r = fetch(app_id)
        apps[slug] = {
            "id": app_id,
            "name": r["trackName"],
            "url": r["trackViewUrl"].split("?")[0],
            "rating": round(r.get("averageUserRating", 0), 2),
            "ratingCount": r.get("userRatingCount", 0),
            "version": r["version"],
            "updated": r["currentVersionReleaseDate"][:10],
            "firstReleased": r["releaseDate"][:10],
            "sizeMB": round(int(r["fileSizeBytes"]) / 1e6, 1),
            "minOS": r["minimumOsVersion"],
            "price": r.get("formattedPrice", ""),
            "category": r["primaryGenreName"],
            "ageRating": r.get("contentAdvisoryRating", ""),
            "languages": r.get("languageCodesISO2A", []),
            "screenshots": {"ios": ios_screenshots(r), "android": []},
        }
        if slug in PLAY_IDS:
            try:
                apps[slug]["screenshots"]["android"] = play_screenshots(PLAY_IDS[slug])
            except Exception as e:  # keep the last good set if Google Play is unreachable or changes
                print("play fetch failed for", slug, e)
            if not apps[slug]["screenshots"]["android"]:
                apps[slug]["screenshots"]["android"] = previous.get(slug, {}).get("screenshots", {}).get("android", [])
    out = {"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "country": COUNTRY, "apps": apps}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "appstore.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("updated", len(apps), "apps")


if __name__ == "__main__":
    main()
