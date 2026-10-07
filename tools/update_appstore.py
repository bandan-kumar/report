"""Refresh data/appstore.json from the public App Store lookup API (no key needed)."""
import json, os, urllib.request
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


def fetch(app_id):
    url = f"https://itunes.apple.com/lookup?id={app_id}&country={COUNTRY}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["results"][0]


def main():
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
        }
    out = {"fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "country": COUNTRY, "apps": apps}
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "appstore.json"), "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print("updated", len(apps), "apps")


if __name__ == "__main__":
    main()
