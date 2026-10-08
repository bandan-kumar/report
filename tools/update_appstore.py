"""Refresh data/appstore.json from the public App Store lookup API (no key needed)."""
import json, os, re, struct, time, urllib.parse, urllib.request
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
# Plain phrases people type into the App Store. Brand names and the keyword field itself are deliberately not listed.
KEYWORDS = {
    "dietplan": [
        "diet plan", "7 day diet plan", "diet planner", "weight loss diet", "weight loss plan",
        "diet plan weight loss", "meal planner for weight loss", "healthy meal planner", "weight loss planner", "meal planner",
    ],
    "upkee": [
        "house cleaning schedule", "cleaning schedule", "cleaning schedule app", "house cleaning", "housework",
        "house cleaning checklist free", "house cleaning app", "weekly cleaning schedule", "cleaning planner", "adhd cleaning checklist",
    ],
}
SEARCH_PAUSE = 3  # seconds between searches: Apple allows roughly 20 requests a minute
HISTORY_DAYS = 365

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


def search_rank(term, app_id):
    """Position of the app in App Store search results for `term` (US, top 200), or None if absent."""
    query = urllib.parse.urlencode({"term": term, "entity": "software", "country": COUNTRY, "limit": 200})
    req = urllib.request.Request(f"https://itunes.apple.com/search?{query}", headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                results = json.load(resp)["results"]
            for position, item in enumerate(results, 1):
                if item.get("trackId") == app_id:
                    return position
            return None
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"search failed for {term!r}")


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


def update_history(out):
    """Append today's numbers to data/history.json (one entry per day, last HISTORY_DAYS kept)."""
    path = os.path.join(ROOT, "data", "history.json")
    try:
        with open(path) as f:
            history = json.load(f)
    except (OSError, ValueError):
        history = []
    entry = {"date": out["fetched"], "apps": {}}
    for slug, a in out["apps"].items():
        entry["apps"][slug] = {
            "rating": a["rating"], "ratingCount": a["ratingCount"], "version": a["version"],
            "ranks": {k["term"]: k["rank"] for k in a.get("keywords", [])},
        }
    history = [h for h in history if h.get("date") != entry["date"]] + [entry]
    with open(path, "w") as f:
        json.dump(history[-HISTORY_DAYS:], f, indent=1)
        f.write("\n")


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
    for slug, terms in KEYWORDS.items():
        last = {k["term"]: k["rank"] for k in previous.get(slug, {}).get("keywords", [])}
        ranked = []
        for term in terms:
            try:
                rank = search_rank(term, IDS[slug])
            except Exception as e:  # keep the last known value rather than failing the whole run
                print("rank lookup failed for", slug, term, e)
                rank = last.get(term)
            ranked.append({"term": term, "rank": rank})
            time.sleep(SEARCH_PAUSE)
        apps[slug]["keywords"] = ranked

    out = {"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "country": COUNTRY, "apps": apps}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "appstore.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    update_history(out)
    print("updated", len(apps), "apps")


if __name__ == "__main__":
    main()
