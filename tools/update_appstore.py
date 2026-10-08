"""Refresh data/appstore.json from public App Store and Google Play data (no keys needed)."""
import json, os, re, statistics, struct, time, urllib.parse, urllib.request
from datetime import date, datetime, timezone

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
        "house cleaning checklist free", "house cleaning app", "weekly cleaning schedule", "home cleaning schedule free", "home chores",
    ],
}
# The phrases whose search neighbours count as "competitors". Only medians are stored, never app names.
COMPARE = {
    "dietplan": ["diet plan", "meal planner", "weight loss diet"],
    "upkee": ["house cleaning schedule", "cleaning schedule"],
}
COMPARE_TOP = 12
SEARCH_PAUSE = 3  # seconds between searches: Apple allows roughly 20 requests a minute
HISTORY_DAYS = 365

PLAY_IDS = {
    "dietplan": "com.pixsterstudio.dietplans",
    "caloric": "com.pixsterstudio.caloric",
    "locateus": "com.pixsterstudio.locationtracker",
    "keto": "com.diet.pixsterstudio.ketodietican",
}

_SEARCHES = {}  # phrase -> results, so a phrase used for ranking and comparing is searched once


def fetch(app_id):
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={COUNTRY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["results"][0]


def search_results(term):
    """Top 200 App Store search results for `term` (US). Cached for the run, retried on failure."""
    if term in _SEARCHES:
        return _SEARCHES[term]
    query = urllib.parse.urlencode({"term": term, "entity": "software", "country": COUNTRY, "limit": 200})
    req = urllib.request.Request(f"https://itunes.apple.com/search?{query}", headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                results = json.load(resp)["results"]
            _SEARCHES[term] = results
            time.sleep(SEARCH_PAUSE)
            return results
        except Exception:
            time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"search failed for {term!r}")


def search_rank(term, app_id):
    """Position of the app in App Store search results for `term`, or None if it is not in the top 200."""
    for position, item in enumerate(search_results(term), 1):
        if item.get("trackId") == app_id:
            return position
    return None


def competitor_medians(slug):
    """Medians across the apps ranking beside this one for its main phrases (no names kept)."""
    seen = {}
    for term in COMPARE[slug]:
        for item in search_results(term)[:COMPARE_TOP]:
            if item.get("trackId") != IDS[slug]:
                seen[item["trackId"]] = item
    items = list(seen.values())
    today = date.today()
    days = [(today - date.fromisoformat(i["currentVersionReleaseDate"][:10])).days for i in items]
    rated = [i for i in items if i.get("userRatingCount", 0) >= 50]
    return {
        "n": len(items),
        "phrases": COMPARE[slug],
        "rating": round(statistics.median(i["averageUserRating"] for i in rated), 2) if rated else None,
        "ratingCount": int(statistics.median(i.get("userRatingCount", 0) for i in items)),
        "daysSinceUpdate": int(statistics.median(days)),
        "languages": statistics.median(len(i.get("languageCodesISO2A", [])) for i in items),
        "sizeMB": round(statistics.median(int(i.get("fileSizeBytes", 0)) / 1e6 for i in items)),
        "updatedWithin14Days": sum(d <= 14 for d in days),
    }


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


def play_page(package):
    url = f"https://play.google.com/store/apps/details?id={package}&hl=en&gl={COUNTRY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def play_screenshots(page):
    """Phone screenshot URLs from a Google Play page. Returns [] if the page layout changes."""
    seen, out = set(), []
    for tag in re.findall(r'<img[^>]+alt="Screenshot image"[^>]*>', page):
        m = re.search(r'(?:src|data-src)="(https://play-lh\.googleusercontent\.com/[^"=]+)=', tag)
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
            shot = m.group(1) + "=w360-h640"
            if is_phone_shot(shot):
                out.append(shot)
    return out


def play_stats(page):
    """Rating, review count text and install bracket from a Google Play page; None where not found."""
    rating = re.search(r"Rated ([0-9.]+) stars out of five", page)
    installs = re.search(r">([0-9][0-9.,]*[KMB]?\+)<", page)
    reviews = re.search(r"([0-9][0-9.,]*[KM]?) reviews", page)
    if not (rating and installs):
        return None
    return {
        "rating": float(rating.group(1)),
        "reviews": reviews.group(1) if reviews else None,
        "installs": installs.group(1),
    }


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
        row = {
            "rating": a["rating"], "ratingCount": a["ratingCount"], "version": a["version"],
            "ranks": {k["term"]: k["rank"] for k in a.get("keywords", [])},
        }
        if a.get("android"):
            row["android"] = a["android"]
        entry["apps"][slug] = row
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
            old = previous.get(slug, {})
            try:
                page = play_page(PLAY_IDS[slug])
                apps[slug]["screenshots"]["android"] = play_screenshots(page)
                apps[slug]["android"] = play_stats(page)
            except Exception as e:  # keep the last good values if Google Play is unreachable or changes
                print("play fetch failed for", slug, e)
            if not apps[slug]["screenshots"]["android"]:
                apps[slug]["screenshots"]["android"] = old.get("screenshots", {}).get("android", [])
            if not apps[slug].get("android") and old.get("android"):
                apps[slug]["android"] = old["android"]
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
        apps[slug]["keywords"] = ranked
    for slug in COMPARE:
        try:
            apps[slug]["compare"] = competitor_medians(slug)
        except Exception as e:
            print("comparison failed for", slug, e)
            if previous.get(slug, {}).get("compare"):
                apps[slug]["compare"] = previous[slug]["compare"]

    out = {"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "country": COUNTRY, "apps": apps}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "appstore.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    update_history(out)
    print("updated", len(apps), "apps")


if __name__ == "__main__":
    main()
