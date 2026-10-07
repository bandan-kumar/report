import os, html, json
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = json.load(open(os.path.join(ROOT, "data", "appstore.json")))
STORE_APPS = STORE["apps"]
LANG_NAMES = {"EN": "English", "FR": "French", "DE": "German", "IT": "Italian", "ES": "Spanish", "NL": "Dutch",
              "JA": "Japanese", "TR": "Turkish", "PT": "Portuguese", "RU": "Russian", "HI": "Hindi", "ZH": "Chinese",
              "KO": "Korean", "AR": "Arabic", "SV": "Swedish", "DA": "Danish", "NB": "Norwegian", "FI": "Finnish",
              "PL": "Polish", "TH": "Thai", "ID": "Indonesian", "VI": "Vietnamese", "HE": "Hebrew", "EL": "Greek"}


def fmt_date(iso, with_day=True):
    d = date.fromisoformat(iso)
    return d.strftime("%-d %b %Y") if with_day else d.strftime("%b %Y")


def fmt_int(n):
    return f"{n:,}"

FAVICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='9' fill='%231e5fb0'/%3E%3Ctext x='16' y='22' font-size='16' font-weight='800' text-anchor='middle' fill='white' font-family='Arial'%3EBK%3C/text%3E%3C/svg%3E"

def icon(path, name):
    return f'<svg class="icon" aria-hidden="true"><use href="{path}assets/icons.svg#{name}"/></svg>'

APPS = [
    dict(slug="dietplan", langs=['English', 'German', 'Spanish', 'French', 'Hindi', 'Italian', 'Japanese', 'Portuguese (Brazil)', 'Russian'], strings='956', name="DietPlan", letter="D", cls="diet", role="primary", tier="Autonomous", play="https://play.google.com/store/apps/details?id=com.pixsterstudio.dietplans",
         status=("live", "Live"),
         platform="iOS",
         summary="AI meal plans, recipes, weight tracking and reminders. An older version is already live. The rebuilt version was feature-complete on 8 Sep 2026 and is waiting on the premium screens before its App Store release.",
         metrics=[("14", "modules & features"), ("89.3 MB", "app size, down from ~140"), ("23/23", "QA items resolved")],
         tags=["Firebase", "Gemini", "HealthKit", "App Attest"],
         reviews=[("q3-2026/#dietplan", "Q3 2026", "Built end to end in about seven weeks, with an AI backend secured by App Attest.")],
         q3=[
            "Built every module end to end: onboarding, meal plans and recipes, weight tracking, reminders, Apple Health and universal links.",
            "Rebuilt the meal and recipe dataset using the EatFirst API and AI generation, with no scraper to maintain.",
            "Cut the app size from about 140 MB to 89.3 MB with On-Demand Resources and a split database.",
            "Added AI meal plans on a dedicated Cloud Function, protected by App Attest, a model allow-list, token limits and daily cost logs.",
            "Closed all 23 QA items and all 23 team-lead review points.",
         ],
         next=["Integrate the new premium screens once design is final.", "Launch the new version on the App Store."]),
    dict(slug="upkee", langs=['English', 'German', 'Spanish', 'French', 'Italian', 'Japanese', 'Dutch', 'Turkish'], strings='2,226', name="Upkee", letter="U", cls="upk", role="primary", tier="Guided", play="", android="In development",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
    dict(slug="caloric", langs=['English'], strings='', name="Caloric", letter="C", cls="cal", role="backup", tier="Autonomous", play="https://play.google.com/store/apps/details?id=com.pixsterstudio.caloric",
         status=("live", "Live"),
         platform="iOS",
         summary="Released in Q3 after fixes to subscriptions and offers, the backend Cloud Function and a sign-out bug that deleted user data.",
         metrics=[("3", "areas fixed before release"), ("Q3", "quarter of release"), ("Fixed", "sign-out data loss")],
         tags=["Subscriptions", "Cloud Functions", "Auth"],
         reviews=[("q3-2026/#caloric", "Q3 2026", "Premium and offers, backend wiring and sign-out fixes that got the app released.")],
         q3=[
            "Fixed the premium screen UI and a screen that would not dismiss.",
            "Made restore and auto-restore purchases work, and stopped the offer screen showing after logout or in the review build.",
            "Connected the app properly to a Cloud Function that had been created but not wired in.",
            "Fixed sign-out, which asked users to log in again and then deleted their data.",
         ],
         next=[]),
    dict(slug="locateus", langs=['English'], strings='', name="LocateUs", letter="L", cls="loc", role="backup", tier="Guided", play="https://play.google.com/store/apps/details?id=com.pixsterstudio.locationtracker",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
    dict(slug="keto", langs=[], strings='', name="Keto", letter="K", cls="keto", role="backup", tier="Guided", play="https://play.google.com/store/apps/details?id=com.diet.pixsterstudio.ketodietican",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
]

for _a in APPS:
    _st = STORE_APPS.get(_a["slug"])
    _a["store"] = _st
    _a["platform"] = "iOS · Android" if _a.get("play") else "iOS"
    if _st:
        if not _a["summary"]:
            _a["summary"] = (f"On the App Store since {fmt_date(_st['firstReleased'], False)} "
                             f"as \"{_st['name']}\" ({_st['category']}).")
        _a["card_metrics"] = [
            (f"{_st['rating']:.1f} ★", f"{fmt_int(_st['ratingCount'])} ratings"),
            (f"v{_st['version']}", "on the App Store"),
            (fmt_date(_st["updated"], False), "last updated"),
        ]
    else:
        _a["card_metrics"] = _a["metrics"]

HEAD = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="color-scheme" content="light dark">
  <link rel="icon" href="{fav}">
  <link rel="stylesheet" href="{p}assets/style.css?v=3">
  <script src="{p}assets/theme.js?v=3"></script>
</head>
<body>
"""

def topbar(p, home=False):
    left = (f'<a class="brand" href="./"><span class="mark">BK</span> Bandan Kumar</a>' if home else
            f'<a class="btn" href="{p}" data-back>{icon(p, "arrow-left")} <span>Apps</span></a>')
    return f"""  <header class="topbar">
    <div class="wrap">
      {left}
      <div class="actions">
        <button class="btn icon-only" type="button" data-theme-toggle aria-label="Switch theme">{icon(p, "moon")}</button>
      </div>
    </div>
  </header>
"""

HAS_IMG = {"dietplan", "caloric", "locateus", "upkee", "keto"}

def icon_tile(a, p, extra):
    if a["slug"] in HAS_IMG:
        return f'<div class="app-icon has-img{extra}" aria-hidden="true"><img src="{p}assets/apps/{a["slug"]}.png" alt="" width="256" height="256"></div>'
    return f'<div class="app-icon {a["cls"]}{extra}" aria-hidden="true">{a["letter"]}</div>'

def play_button(a, p):
    if a.get("play"):
        return f' <a class="btn" href="{a["play"]}" rel="noopener">View on Google Play {icon(p, "arrow-right")}</a>'
    if a.get("android"):
        return f' <span class="chip pre plain">Android {a["android"].lower()}</span>'
    return ""


def android_line(a):
    if a.get("android"):
        return f'<div class="langline">{icon("", "smartphone")} Android: {a["android"].lower()}</div>'
    return ""


def langline(a):
    n = len(a["store"]["languages"]) if a.get("store") else len(a["langs"])
    if not n:
        return ""
    label = f"{n} languages" if n > 1 else "English only"
    return f'<div class="langline">{icon("", "globe")} {label}</div>'

def chip(kind, text):
    return f'<span class="chip {kind}">{html.escape(text)}</span>'

def role_chip(a):
    return chip("role", f"{'Primary' if a['role'] == 'primary' else 'Backup'} · {a['tier']}")



def app_card(a):
    metrics = ""
    if a["card_metrics"]:
        metrics = '<div class="metrics">' + "".join(
            f'<div class="metric"><b>{html.escape(b)}</b><span>{html.escape(s)}</span></div>' for b, s in a["card_metrics"]) + "</div>"
    tags = ""
    if a["tags"]:
        tags = '<div class="tags">' + "".join(f'<span class="tag">{html.escape(t)}</span>' for t in a["tags"]) + "</div>"
    plat = f'<div class="platform">{a["platform"]}</div>' if a["platform"] else ""
    return f"""          <article class="card app">
            <div class="app-top">
              {icon_tile(a, '', '')}
              <div>
                <h3><a href="apps/{a['slug']}/">{a['name']}</a></h3>
                {plat}
              </div>
              <div class="status-line">{chip(*a['status'])}</div>
            </div>
            <p>{html.escape(a['summary'])}</p>
            {metrics}
            {tags}
            {langline(a)}
            {android_line(a)}
            <span class="go">View review {icon('', 'arrow-right')}</span>
          </article>
"""

def build_index():
    prim = "\n".join(app_card(a) for a in APPS if a["role"] == "primary")
    sec = "\n".join(app_card(a) for a in APPS if a["role"] == "backup")
    s = HEAD.format(title="Bandan Kumar · Apps &amp; Reviews", p="", fav=FAVICON,
                    desc="The apps Bandan Kumar builds and supports, with a review page for each and the quarterly reports.")
    s += topbar("", home=True)
    s += f"""
  <main>
    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Product Engineer</p>
        <h1>Apps I build, ship<br>and review.</h1>
        <p class="lead">Two apps I own end to end and three I back up. Each has its own review: where it stands today, what changed, and what comes next.</p>
      </div>
    </section>

    <section class="section" id="apps">
      <div class="wrap">
        <div class="section-head">
          <h2>Apps</h2>
          <p>Live App Store data as of {fmt_date(STORE["fetched"])}</p>
        </div>

        <div class="group">
          <div class="group-head"><h3>Primary</h3><p>Apps I own and develop.</p></div>
          <div class="grid apps">
{prim}          </div>
        </div>

        <div class="group">
          <div class="group-head"><h3>Backup</h3><p>Apps I cover when the primary is unavailable.</p></div>
          <div class="grid apps">
{sec}          </div>
        </div>
      </div>
    </section>

    <section class="section" id="reports">
      <div class="wrap">
        <div class="section-head">
          <h2>Quarterly reviews</h2>
          <p>Across all apps. Open a report, or print it as a clean PDF.</p>
        </div>

        <div class="grid reports">
          <article class="card report">
            <div class="ico">{icon('', 'file-text')}</div>
            <div>
              <span class="chip plain">July – September 2026</span>
              <h3 style="margin-top:10px">Q3 2026 Performance Review</h3>
            </div>
            <p>What shipped, what changed, the challenges along the way, and what is next.</p>
            <div class="row">
              <a class="btn primary" href="q3-2026/">View report {icon('', 'arrow-right')}</a>
              <a class="btn" href="q3-2026/Bandan-Kumar-Q3-2026-Review.pdf" download>{icon('', 'download')} PDF</a>
            </div>
          </article>

          <article class="card report">
            <div class="ico">{icon('', 'target')}</div>
            <div>
              <span class="chip plain">October – December 2026</span>
              <h3 style="margin-top:10px">Q4 2026 Planning</h3>
            </div>
            <p>Focus, first actions and the numbers to track for each app: ASO, conversion, onboarding completion and paywall conversion.</p>
            <div class="row">
              <a class="btn primary" href="q4-2026/">View plan {icon('', 'arrow-right')}</a>
            </div>
          </article>
        </div>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="wrap">© 2026 Bandan Kumar</div>
  </footer>
</body>
</html>
"""
    open(f"{ROOT}/index.html", "w").write(s)

def build_app(a):
    p = "../../"
    s = HEAD.format(title=f"{a['name']} · Review · Bandan Kumar", p=p, fav=FAVICON,
                    desc=f"{a['name']}: status, quarterly reviews and focus areas.")
    s += topbar(p)
    plat = f" · {a['platform']}" if a["platform"] else ""
    s += f"""
  <main>
    <section class="app-hero-wrap">
      <div class="wrap app-hero">
        {icon_tile(a, p, ' lg')}
        <div>
          <h1>{a['name']}</h1>
          <div class="chips">{chip(*a['status'])} {role_chip(a)}{'<span class="tag">' + a['platform'] + '</span>' if a['platform'] else ''}</div>
        </div>
      </div>
      <div class="wrap"><p class="lead" style="margin-top:18px;color:var(--muted);max-width:70ch">{html.escape(a['summary'])}</p></div>
    </section>

    <div class="wrap">
"""
    st = a.get("store")
    if st:
        boxes = [
            (f"{st['rating']:.1f} ★", "Rating"),
            (fmt_int(st["ratingCount"]), "Ratings"),
            (f"v{st['version']}", "Current version"),
            (fmt_date(st["updated"]), "Last updated"),
            (f"{st['sizeMB']:g} MB", "App size"),
            (f"iOS {st['minOS']}+", "Minimum OS"),
            (st["category"], "Category"),
            (str(len(st["languages"])), "Store languages"),
        ]
        s += ('      <section class="block">\n        <h2>Product &amp; ASO snapshot</h2>\n'
              f'        <p class="sub">From the public App Store listing, US storefront, as of {fmt_date(STORE["fetched"])}.</p>\n'
              '        <div class="grid snapshot">\n'
              + "".join(f'          <div class="card snap has"><b>{html.escape(b)}</b><span>{html.escape(l)}</span></div>\n' for b, l in boxes)
              + '        </div>\n'
              f'        <p class="note stores"><a class="btn" href="{st["url"]}" rel="noopener">View on the App Store {icon(p, "arrow-right")}</a>{play_button(a, p)}</p>\n'
              '        <p class="note">Downloads, impressions and conversion are not public, so they are not shown here.</p>\n'
              '      </section>\n')
    shots = (st or {}).get("screenshots", {})
    if shots.get("ios") or shots.get("android"):
        s += '      <section class="block">\n        <h2>Store screenshots</h2>\n        <p class="sub">As shown on the store listings.</p>\n'
        for label, key in (("App Store", "ios"), ("Google Play", "android")):
            urls = shots.get(key) or []
            if urls:
                s += f'        <h3 class="shots-title">{label}</h3>\n        <div class="gallery" tabindex="0" aria-label="{a["name"]} {label} screenshots, scroll sideways">\n'
                for i, u in enumerate(urls, 1):
                    s += (f'          <figure class="shot"><img class="store" src="{u}" alt="{a["name"]} {label} screenshot {i}" '
                          'loading="lazy" referrerpolicy="no-referrer" width="360" height="640"></figure>\n')
                s += "        </div>\n"
            elif key == "android" and a.get("android"):
                s += f'        <h3 class="shots-title">{label}</h3>\n        <p class="note">Android version {a["android"].lower()}.</p>\n'
        s += "      </section>\n"
    if a["metrics"]:
        s += '      <section class="block">\n        <h2>Delivery highlights</h2>\n        <p class="sub">From the Q3 2026 review.</p>\n        <div class="grid stats">\n'
        for b, l in a["metrics"]:
            s += f'          <div class="card stat"><div class="big">{html.escape(b)}</div><h3>{html.escape(l)}</h3></div>\n'
        s += "        </div>\n      </section>\n"
    store_langs = [LANG_NAMES.get(c, c) for c in st["languages"]] if st else []
    groups = []
    if store_langs:
        groups.append(("On the App Store", f"{len(store_langs)} language" + ("s" if len(store_langs) != 1 else ""), store_langs))
    if a["langs"] and sorted(a["langs"]) != sorted(store_langs):
        sub = f"{len(a['langs'])} languages"
        if a["strings"]:
            sub += f" · {a['strings']} strings"
        groups.append(("In the current project", sub, a["langs"]))
    if groups:
        s += '      <section class="block">\n        <h2>Localization</h2>\n        <p class="sub">&nbsp;</p>\n'
        for title, sub, names in groups:
            s += (f'        <div class="loc-group"><h3>{title} <span>{sub}</span></h3><div class="pills">'
                  + "".join(f'<span class="pill">{html.escape(x)}</span>' for x in names) + '</div></div>\n')
        s += '      </section>\n'
    s += '      <section class="block">\n        <h2>Quarterly reviews</h2>\n        <p class="sub">What changed, quarter by quarter.</p>\n        <div class="rows">\n'
    for href, label, blurb in a["reviews"]:
        s += f"""          <article class="card row-card">
            <div class="ico-sm">{icon(p, 'file-text')}</div>
            <div class="grow"><h3>{label}</h3><p>{html.escape(blurb)}</p></div>
            <a class="btn primary" href="{p}{href}">Open {icon(p, 'arrow-right')}</a>
          </article>
"""
    s += f"""          <article class="card row-card">
            <div class="ico-sm">{icon(p, 'target')}</div>
            <div class="grow"><h3>Q4 2026</h3><p>Focus, first actions and what to measure.</p></div>
            <a class="btn primary" href="{p}q4-2026/#{a['slug']}">Open {icon(p, 'arrow-right')}</a>
          </article>
        </div>
      </section>
"""
    if a["q3"]:
        s += '      <section class="block">\n        <h2>What changed in Q3</h2>\n        <div class="card"><ul class="bullets">\n'
        s += "".join(f"          <li>{html.escape(x)}</li>\n" for x in a["q3"])
        s += "        </ul></div>\n      </section>\n"
    if a["next"]:
        s += '      <section class="block">\n        <h2>Next up</h2>\n        <div class="card"><ul class="bullets">\n'
        s += "".join(f"          <li>{html.escape(x)}</li>\n" for x in a["next"])
        s += "        </ul></div>\n      </section>\n"
    s += """    </div>
  </main>

  <footer class="footer">
    <div class="wrap">© 2026 Bandan Kumar</div>
  </footer>
</body>
</html>
"""
    d = f"{ROOT}/apps/{a['slug']}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w").write(s)


Q4 = {
    "dietplan": dict(
        headline="Launch v2.0 with a refreshed store page and a good first-run experience.",
        why="The live listing shows {rt}★ from {rc} ratings in {nl} store languages. v2.0 is feature-complete with 9 languages and a new UI, and the current store page shows none of that.",
        actions=[
            "Launch v2.0 on the App Store, including the AI meal plans.",
            "Integrate the premium screens once design is final.",
            "Refresh the store page for launch: screenshots from the v2.0 UI, and localized metadata for Hindi, Japanese, Portuguese and Russian.",
            "Read the onboarding funnel from day one using the Q3 analytics events, and fix the biggest drop-off.",
        ],
        test="Screenshot A/B test on the store page. Primary metric: conversion rate.",
        measure=["Onboarding completion", "Conversion rate", "Paywall conversion", "Rating after launch"],
        months=["Premium screens, ASO baseline", "Launch v2.0 with the refreshed store page", "Screenshot test result, first onboarding and paywall read"],
    ),
    "upkee": dict(
        headline="Build up ratings and get the onboarding funnel measured.",
        why="Released in Aug 2026. It has {rt}★ but only {rc} ratings, and {nl} store languages already. The priority is more ratings and more visibility.",
        actions=[
            "Check that onboarding and first-task events are in place, read the funnel, and fix the biggest drop-off.",
            "Ask for a rating after a success moment (a completed cleaning task), and only from happy users.",
            "Review the keyword set and screenshots against what people search for.",
            "Finish the Android version so the app is on both platforms.",
        ],
        test="Screenshot A/B test on the store page. Primary metric: conversion rate.",
        measure=["Onboarding completion", "Conversion rate", "Number of ratings", "Paywall conversion"],
        months=["Funnel events check, ASO baseline, Android build", "Fix the top drop-off, rating prompt and screenshot test live", "Review rating and conversion trend, test result"],
    ),
    "caloric": dict(
        headline="Backup: keep an eye on crashes and reviews.",
        why="{rt}★ from {rc} ratings, English only, last updated {upd} after the Q3 fixes.",
        actions=[
            "Keep an eye on crashes and new reviews, especially for the Q3 fixes (restore purchases, sign-out).",
            "Talk through upcoming features with the primary so I know what is going on in the app.",
            "Suggest localization to the primary, since the app is English only today.",
            "Help with iOS-specific issues when they come up.",
            "Cover urgent bugs and hotfix releases when the primary is unavailable.",
        ],
        measure=["Crash rate", "Rating trend"],
        months=["Watch the Q3 fixes", "Keep an eye on crashes and reviews", "Quarter summary"],
    ),
    "locateus": dict(
        headline="Backup: keep an eye on crashes and reviews.",
        why="{rt}★ from {rc} ratings, English only, last updated {upd}.",
        actions=[
            "Keep an eye on crashes and new reviews.",
            "Talk through upcoming features with the primary so I know what is going on in the app.",
            "Mention the low number of ratings to the primary.",
            "Help with iOS-specific issues when they come up.",
            "Cover urgent bugs and hotfix releases when the primary is unavailable.",
        ],
        measure=["Crash rate", "Rating"],
        months=["Store-page check", "Keep an eye on crashes and reviews", "Quarter summary"],
    ),
    "keto": dict(
        headline="Backup on the app with the most users: stay familiar with it.",
        why="{rt}★ from {rc} ratings and {nl} store languages. It has the largest audience of the five, so a bug here reaches the most people.",
        actions=[
            "Keep an eye on crashes and new reviews.",
            "Talk through upcoming features with the primary so I know what is going on in the app.",
            "Help with iOS-specific issues when they come up.",
            "Cover urgent bugs and hotfix releases when the primary is unavailable.",
        ],
        measure=["Crash rate", "Rating trend"],
        months=["Review-status check", "Keep an eye on crashes and reviews", "Quarter summary"],
    ),
}

FUNNEL = [
    ("search", "Discover", "Impressions and product page views",
     "App Store Connect, App Analytics", "Title, subtitle, keywords"),
    ("download", "Install", "Conversion rate: downloads per page view",
     "App Store Connect, App Analytics", "Screenshots, ratings, localization"),
    ("check-square", "Activate", "Onboarding completion",
     "Firebase Analytics events", "Fewer steps, value shown early"),
    ("award", "Pay", "Paywall conversion",
     "Subscription analytics", "Paywall design, placement, pricing"),
    ("thumbs-up", "Recommend", "Rating and number of ratings",
     "Public App Store listing", "Rating prompt timing, fixing repeat issues"),
]



def build_q4():
    p = "../"
    s = HEAD.format(title="Q4 2026 Planning · Bandan Kumar", p=p, fav=FAVICON,
                    desc="Q4 2026 planning: focus, first actions and the numbers to watch for DietPlan and Upkee, plus backup cover for three more apps.")
    s += f"""  <header class="topbar">
    <div class="wrap">
      <a class="btn" href="{p}" data-back>{icon(p, "arrow-left")} <span>Apps</span></a>
      <div class="actions">
        <button class="btn" type="button" data-print>{icon(p, "printer")} <span class="label-long">Print</span></button>
        <button class="btn icon-only" type="button" data-theme-toggle aria-label="Switch theme">{icon(p, "moon")}</button>
      </div>
    </div>
  </header>

  <header class="report-hero">
    <div class="wrap">
      <p class="eyebrow">Planning</p>
      <h1>Q4 2026 Planning</h1>
      <p class="period">October – December 2026</p>
      <div class="who"><b>Bandan Kumar</b><span>Product Engineer · 2 apps owned, 3 backed up</span></div>
    </div>
  </header>

  <main class="wrap">
    <section class="block">
      <h2>The funnel I own</h2>
      <p class="sub">For DietPlan and Upkee: from store search to a paying, happy user. Each stage has one number to watch and something I can change.</p>
      <div class="grid flow">
"""
    for i, (ico, stage, metric, src, lever) in enumerate(FUNNEL, 1):
        s += f"""        <div class="card step">
          <div class="ico-sm">{icon(p, ico)}</div>
          <p class="stage">{i}. {stage}</p>
          <h3>{metric}</h3>
          <p class="src">{src}</p>
          <p class="lever"><b>I can change:</b> {lever}</p>
        </div>
"""
    s += """      </div>
    </section>

    <section class="block">
      <h2>At a glance</h2>
      <p class="sub">One focus per app.</p>
      <div class="grid glance">
"""
    for a in APPS:
        s += f"""        <a class="card glance-card" href="#{a['slug']}">
          <div class="glance-top">{icon_tile(a, p, '')}<div><h3>{a['name']}</h3>{role_chip(a)}</div></div>
          <p>{html.escape(Q4[a['slug']]['headline'])}</p>
        </a>
"""
    s += """      </div>
    </section>

    <section class="block">
      <h2>App plans</h2>
      <p class="sub">What I will do first, and what I will watch.</p>
      <div class="plans">
"""
    for a in APPS:
        q = Q4[a["slug"]]
        st = a.get("store") or {}
        why = q["why"].format(rt=f"{st.get('rating', 0):.1f}", rc=fmt_int(st.get("ratingCount", 0)),
                              nl=len(st.get("languages", [])), upd=fmt_date(st["updated"]) if st else "")
        backup = a["role"] == "backup"
        s += f"""        <article class="card plan" id="{a['slug']}">
          <div class="plan-head">{icon_tile(a, p, '')}
            <div><h3>{a['name']}</h3><div class="chips">{role_chip(a)}{chip(*a['status'])}</div></div>
          </div>
          <p class="plan-focus">{html.escape(q['headline'])}</p>
          <p class="why">{html.escape(why)}</p>
          <h4>{'If I step in' if backup else 'First actions'}</h4>
          <ul class="bullets">
""" + "".join(f"            <li>{html.escape(x)}</li>\n" for x in q["actions"]) + "          </ul>\n"
        if q.get("test"):
            s += f"          <h4>First test</h4>\n          <p>{html.escape(q['test'])}</p>\n"
        s += """          <h4>Watch</h4>
          <div class="tags">""" + "".join(f'<span class="tag">{html.escape(x)}</span>' for x in q["measure"]) + """</div>
        </article>
"""
    s += """      </div>
    </section>

    <section class="block">
      <h2>Quarter timeline</h2>
      <p class="sub">Month by month: baseline first, then fix, then measure.</p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>App</th><th>October</th><th>November</th><th>December</th></tr></thead>
          <tbody>
"""
    for a in APPS:
        m = Q4[a["slug"]]["months"]
        s += (f'            <tr><td data-label="App">{a["name"]}</td><td data-label="October">{html.escape(m[0])}</td>'
              f'<td data-label="November">{html.escape(m[1])}</td><td data-label="December">{html.escape(m[2])}</td></tr>\n')
    s += """          </tbody>
        </table>
      </div>
    </section>

    <section class="block">
      <h2>Operating rhythm</h2>
      <p class="sub">A small routine that fits alongside development.</p>
      <div class="grid three">
        <div class="card"><h3>Weekly</h3><ul>
          <li>Impressions, page views, conversion and downloads for DietPlan and Upkee</li>
          <li>New reviews on all five apps</li>
          <li>Anything unusual noted the same day</li></ul></div>
        <div class="card"><h3>Monthly</h3><ul>
          <li>Onboarding and paywall funnel for DietPlan and Upkee</li>
          <li>Rating trend and crash-free rate for all five apps</li>
          <li>What each change did to the numbers</li></ul></div>
        <div class="card"><h3>End of quarter</h3><ul>
          <li>ASO and rating movement summary</li>
          <li>What shipped and what it changed</li>
          <li>Draft priorities for Q1 2027</li></ul></div>
      </div>
    </section>

    <section class="block">
      <div class="ahead">
        <h2>What I need</h2>
        <ul>
          <li><span class="ico-sm">""" + icon(p, "award") + """</span><span>Final design for the DietPlan premium screens</span></li>
          <li><span class="ico-sm">""" + icon(p, "calendar") + """</span><span>A target launch date for DietPlan v2.0</span></li>
          <li><span class="ico-sm">""" + icon(p, "search") + """</span><span>App Store Connect analytics access for DietPlan and Upkee</span></li>
        </ul>
      </div>
    </section>

    <p class="print-only print-foot">Bandan Kumar · Q4 2026 Planning · App Store figures as of """ + fmt_date(STORE["fetched"]) + """</p>
  </main>

  <footer class="footer no-print">
    <div class="wrap">© 2026 Bandan Kumar · App Store figures as of """ + fmt_date(STORE["fetched"]) + """</div>
  </footer>
</body>
</html>
"""
    d = f"{ROOT}/q4-2026"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/index.html", "w").write(s)


build_index()
build_q4()
for a in APPS:
    build_app(a)
print("built", len(APPS), "apps")
