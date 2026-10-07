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
    dict(slug="dietplan", langs=['English', 'German', 'Spanish', 'French', 'Hindi', 'Italian', 'Japanese', 'Portuguese (Brazil)', 'Russian'], strings='956', name="DietPlan", letter="D", cls="diet", role="primary",
         status=("live", "Live"),
         platform="iOS",
         summary="AI-powered meal plans, recipes, weight tracking and reminders. An earlier version is already live; the rebuilt version was feature-complete on 8 Sep 2026 and is heading for its App Store release.",
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
    dict(slug="upkee", langs=['English', 'German', 'Spanish', 'French', 'Italian', 'Japanese', 'Dutch', 'Turkish'], strings='2,226', name="Upkee", letter="U", cls="upk", role="primary",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
    dict(slug="caloric", langs=['English'], strings='', name="Caloric", letter="C", cls="cal", role="secondary",
         status=("live", "Live"),
         platform="iOS",
         summary="Secondary developer. Released in Q3 after key fixes across subscriptions and offers, the backend Cloud Function, and a sign-out flow that used to delete user data.",
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
    dict(slug="locateus", langs=['English'], strings='', name="LocateUs", letter="L", cls="loc", role="secondary",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
    dict(slug="keto", langs=[], strings='', name="Keto", letter="K", cls="keto", role="secondary",
         status=("live", "Live"),
         platform="iOS",
         summary="",
         metrics=[], tags=[], reviews=[], q3=[], next=[]),
]

for _a in APPS:
    _st = STORE_APPS.get(_a["slug"])
    _a["store"] = _st
    if _st:
        if not _a["summary"]:
            role = "Primary developer." if _a["role"] == "primary" else "Secondary developer."
            _a["summary"] = (f"{_st['name']}: a {_st['category']} app on the App Store since "
                             f"{fmt_date(_st['firstReleased'], False)}. {role}")
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
  <link rel="stylesheet" href="{p}assets/style.css">
  <script src="{p}assets/theme.js"></script>
</head>
<body>
"""

def topbar(p, home=False):
    left = (f'<a class="brand" href="./"><span class="mark">BK</span> Bandan Kumar</a>' if home else
            f'<a class="btn" href="{p}">{icon(p, "arrow-left")} <span>Apps</span></a>')
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

def langline(a):
    n = len(a["store"]["languages"]) if a.get("store") else len(a["langs"])
    if not n:
        return ""
    label = f"{n} languages" if n > 1 else "English only"
    return f'<div class="langline">{icon("", "globe")} {label}</div>'

def chip(kind, text):
    return f'<span class="chip {kind}">{html.escape(text)}</span>'

def role_chip(a):
    return chip("role", "Primary developer" if a["role"] == "primary" else "Secondary developer")

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
            <span class="go">View review {icon('', 'arrow-right')}</span>
          </article>
"""

def build_index():
    prim = "\n".join(app_card(a) for a in APPS if a["role"] == "primary")
    sec = "\n".join(app_card(a) for a in APPS if a["role"] == "secondary")
    s = HEAD.format(title="Bandan Kumar · Apps &amp; Reviews", p="", fav=FAVICON,
                    desc="The apps Bandan Kumar builds and supports, with a review page for each and the quarterly reports.")
    s += topbar("", home=True)
    s += f"""
  <main>
    <section class="hero">
      <div class="wrap">
        <p class="eyebrow">Product Engineer</p>
        <h1>Apps I build, ship<br>and review.</h1>
        <p class="lead">Five apps, each with its own review: where it stands today, what changed, and what comes next.</p>
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
          <div class="group-head"><h3>Secondary</h3><p>Apps I cover when the primary developer is unavailable and something urgent needs doing.</p></div>
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

          <article class="card report soon">
            <div class="ico">{icon('', 'target')}</div>
            <div>
              <span class="chip pre plain">Coming soon</span>
              <h3 style="margin-top:10px">Q4 2026 Plan</h3>
            </div>
            <p>Product and ASO status, the main opportunity for each app, and what to focus on first.</p>
            <div class="row">
              <a class="btn" href="#reports" aria-disabled="true" tabindex="-1">Not published yet</a>
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
              f'        <p class="note"><a class="btn" href="{st["url"]}" rel="noopener">View on the App Store {icon(p, "arrow-right")}</a></p>\n'
              '        <p class="note">Downloads, impressions and conversion are not public, so they are not shown here.</p>\n'
              '      </section>\n')
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
            <div class="grow"><h3>Q4 2026</h3><p>Plan and focus areas. Not published yet.</p></div>
            <span class="chip pre plain">Coming soon</span>
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

build_index()
for a in APPS:
    build_app(a)
print("built", len(APPS), "apps")
