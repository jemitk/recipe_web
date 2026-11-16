#!/usr/bin/env python3
"""Builds the website into the dist/ folder.

Reads recipes from content/recipes/*.md (English) and content/recipes/ko/*.md (Korean),
and writes plain HTML pages. Run:  python3 build.py
"""
import html, json, pathlib, re, shutil

ROOT = pathlib.Path(__file__).parent
DIST = ROOT / "dist"
CFG = json.loads((ROOT / "site.json").read_text())
SITE = CFG["site_name"]
TARGET_KCAL = 600
e = html.escape

T = {
    "en": dict(
        recipes="Recipes", about="About", light="Light", dark="Dark", dark_mode="Dark mode",
        hero_title="Dinners that fill you up and add up.",
        hero_sub="Home-cooked meals from many kitchens, each built to the same three numbers.",
        per_serving="kcal per serving", protein="protein", fiber="fiber", per_serving_label="Per serving",
        filter_label="Filter recipes",
        filters=[("all", "All"), ("u600", "600 kcal or less"), ("p40", "40 g+ protein"), ("f15", "15 g+ fiber"),
                 ("chicken", "Chicken"), ("beef", "Beef"), ("fish", "Fish"), ("plant", "Plant-based"),
                 ("prep", "Meal prep"), ("freezer", "Freezer-friendly")],
        count_all="{n} recipes", count_some="{a} of {n} recipes", none="No recipes match this filter yet.",
        serves="serves {n}", photo="Photo coming", back="← All recipes",
        ingredients="Ingredients", method="Method", notes="Notes",
        meets="Meets all three targets.", over="{n} kcal over the 600 target. Protein and fiber targets met.",
        foot="Nutrition figures are estimates per serving.", language="Language",
        about_title="About the cook", draft="Draft text for layout only. Replace with your own story.",
        about_lead="I'm Karen. I cook dinners that taste like a treat and still fit three numbers: around 600 calories, at least 30 grams of protein and at least 10 grams of fiber.",
        about_body="Every recipe here is one I make at home, tested as meal prep for two. I borrow from Turkish, Ethiopian, Vietnamese, Chinese and Tex-Mex cooking, and I lean on lentils, beans and vegetables to get the fiber up.",
        services=["Recipe development", "Weekly meal prep plans", "Private dinners"], example="Example service",
        your_photo="Your photo",
        home_desc="Healthy home-cooked dinners around 600 calories with at least 30 g protein and 10 g fiber.",
    ),
    "ko": dict(
        recipes="레시피", about="소개", light="라이트", dark="다크", dark_mode="다크 모드",
        hero_title="든든하게 먹고, 숫자까지 딱 맞는 저녁.",
        hero_sub="여러 나라의 집밥을 똑같은 세 가지 숫자에 맞춰 만들었어요.",
        per_serving="kcal (1인분)", protein="단백질", fiber="식이섬유", per_serving_label="1인분 기준",
        filter_label="레시피 필터",
        filters=[("all", "전체"), ("u600", "600kcal 이하"), ("p40", "단백질 40g 이상"), ("f15", "식이섬유 15g 이상"),
                 ("chicken", "닭고기"), ("beef", "소고기"), ("fish", "생선"), ("plant", "식물성"),
                 ("prep", "밀프렙"), ("freezer", "냉동 보관 가능")],
        count_all="레시피 {n}개", count_some="레시피 {n}개 중 {a}개", none="이 조건에 맞는 레시피가 아직 없어요.",
        serves="{n}인분", photo="사진 준비 중", back="← 전체 레시피",
        ingredients="재료", method="만드는 법", notes="메모",
        meets="세 가지 목표를 모두 충족해요.", over="목표 600kcal보다 {n}kcal 높아요. 단백질과 식이섬유 목표는 충족해요.",
        foot="영양 정보는 1인분 기준 추정치입니다.", language="언어",
        about_title="요리하는 사람", draft="레이아웃 확인용 임시 글입니다. 직접 쓴 이야기로 바꿔 주세요.",
        about_lead="안녕하세요, Karen입니다. 맛있으면서도 세 가지 숫자에 맞는 저녁을 만들어요. 약 600칼로리, 단백질 30g 이상, 식이섬유 10g 이상.",
        about_body="여기 있는 레시피는 모두 집에서 직접 만들고 2인분 밀프렙으로 확인한 것들이에요. 터키, 에티오피아, 베트남, 중국, 텍스멕스 요리에서 아이디어를 얻고, 렌틸콩과 콩, 채소로 식이섬유를 채워요.",
        services=["레시피 개발", "주간 밀프렙 플랜", "프라이빗 디너"], example="예시 서비스",
        your_photo="프로필 사진",
        home_desc="약 600칼로리, 단백질 30g 이상, 식이섬유 10g 이상에 맞춘 건강한 집밥 저녁 레시피.",
    ),
}


def parse(path):
    _, fm, body = path.read_text(encoding="utf-8").split("---", 2)
    meta = {}
    for line in fm.strip().splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = re.sub(r"\s{2,}#.*$", "", v).strip()
    groups, steps, notes, sec, cur = [], [], [], None, None
    for line in body.splitlines():
        s = line.strip()
        if s.startswith("## "):
            sec, cur = s[3:].lower(), None
        elif s.startswith("### ") and sec == "ingredients":
            cur = {"name": re.sub(r"\s*\(.*\)$", "", s[4:]), "items": []}
            groups.append(cur)
        elif s.startswith("- "):
            item = s[2:]
            if sec == "ingredients":
                if item.startswith("TODO"):
                    item = "Bolognese sauce, 1 serving (recipe to be added)"
                if cur is None:
                    cur = {"name": "", "items": []}
                    groups.append(cur)
                cur["items"].append(item)
            elif sec == "notes":
                notes.append(item)
        elif re.match(r"\d+\. ", s) and sec == "method":
            steps.append(re.sub(r"^\d+\. ", "", s))
    src = meta.get("source", "")
    m = re.search(r"\((https?://[^)]+)\)", src)
    text = dict(title=meta["title"], desc=meta["description"], cuisine=meta.get("cuisine", ""),
                groups=groups, steps=steps, notes=notes,
                source=re.sub(r"\s*\(https?://[^)]+\)", "", src), source_url=m.group(1) if m else "")
    return meta, text


def load():
    out = []
    rdir = ROOT / "content" / "recipes"
    for p in sorted(rdir.glob("*.md")):
        if p.name in ("README.md", "_TEMPLATE.md"):
            continue
        meta, en = parse(p)
        tags = [t.strip() for t in meta.get("tags", "[]").strip("[]").split(",") if t.strip()]
        rec = dict(slug=p.stem, serves=int(meta["servings"]), kcal=int(meta["calories"]),
                   protein=int(meta["protein_g"]), fiber=int(meta["fiber_g"]),
                   main=meta.get("main_protein", ""), tags=tags, photo=meta.get("photo", ""),
                   date=meta.get("date_added", ""), en=en, ko=en)
        kp = rdir / "ko" / p.name
        if kp.exists():
            rec["ko"] = parse(kp)[1]
        out.append(rec)
    return out


def page(lang, depth, path_en, path_ko, title, desc, body, current, extra_head=""):
    """depth = how many folders deep this page is from the site root."""
    t = T[lang]
    up = "../" * depth
    home = up + ("ko/" if lang == "ko" else "")
    full_title = SITE if not title else f"{title} | {SITE}"
    cur = lambda k: ' aria-current="page"' if current == k else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="alternate" hreflang="en" href="{up}{path_en}">
<link rel="alternate" hreflang="ko" href="{up}{path_ko}">
<script>try{{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{up}assets/site.css">
{extra_head}</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="{home or './'}" lang="en">{e(SITE)}</a>
    <nav class="nav" aria-label="Main">
      <a href="{home or './'}"{cur('recipes')}>{t['recipes']}</a>
      <a href="{home}about/"{cur('about')}>{t['about']}</a>
      <span class="theme"><span class="label">{t['light']}</span><button class="switch" id="theme-toggle" type="button" role="switch" aria-checked="false" aria-label="{t['dark_mode']}"><i></i></button><span class="label">{t['dark']}</span></span>
    </nav>
  </header>
  <main>
{body}
  </main>
  <footer class="foot">
    <div class="footrow">
      <p>{t['foot']}</p>
      <div class="lang" role="group" aria-label="{t['language']}">
        <a href="{up}{path_en or './'}" data-set-lang="en" lang="en" aria-current="{'true' if lang == 'en' else 'false'}">EN</a><span aria-hidden="true">|</span><a href="{up}{path_ko}" data-set-lang="ko" lang="ko" aria-current="{'true' if lang == 'ko' else 'false'}">KR</a>
      </div>
    </div>
  </footer>
</div>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""


def nums(r, t):
    return (f'<div class="nums"><span>{r["kcal"]} <span>kcal</span></span>'
            f'<span>{r["protein"]} g <span>{t["protein"]}</span></span>'
            f'<span>{r["fiber"]} g <span>{t["fiber"]}</span></span></div>')


def picture(r, i, t, up, alt):
    if r["photo"]:
        return f'<div class="plate"><img src="{up}assets/photos/{e(r["photo"])}" alt="{e(alt)}" loading="lazy" style="width:100%;height:100%;object-fit:cover"></div>'
    return f'<div class="plate t{i % 3}"><i></i><span class="label">{t["photo"]}</span></div>'


def home(lang, recipes):
    t = T[lang]
    n = len(recipes)
    chips = "".join(f'<button class="chip" type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{label}</button>' for k, label in t["filters"])
    cards = "".join(f"""
      <a class="card" href="recipes/{r['slug']}/" data-kcal="{r['kcal']}" data-protein="{r['protein']}" data-fiber="{r['fiber']}" data-main="{r['main']}" data-tags="{' '.join(r['tags'])}">
        {picture(r, i, t, '../' if lang == 'ko' else '', r[lang]['title'])}
        <div class="sub">{e(r[lang]['cuisine'])} · {t['serves'].format(n=r['serves'])}</div>
        <h3>{e(r[lang]['title'])}</h3>
        {nums(r, t)}
      </a>""" for i, r in enumerate(recipes))
    body = f"""    <section class="hero">
      <h1>{t['hero_title']}</h1>
      <p>{t['hero_sub']}</p>
      <div class="rule">
        <div><b>~600</b><span>{t['per_serving']}</span></div>
        <div><b>30 g+</b><span>{t['protein']}</span></div>
        <div><b>10 g+</b><span>{t['fiber']}</span></div>
      </div>
    </section>
    <div class="filters" role="group" aria-label="{t['filter_label']}">{chips}</div>
    <p class="count" id="count" data-all="{t['count_all'].format(n=n)}" data-some="{t['count_some'].format(a='{a}', n=n)}">{t['count_all'].format(n=n)}</p>
    <p id="none" hidden>{t['none']}</p>
    <section class="grid">{cards}
    </section>"""
    depth = 1 if lang == "ko" else 0
    return page(lang, depth, "", "ko/", "", t["home_desc"], body, "recipes")


def recipe_page(lang, r, i):
    t, c = T[lang], r[lang]
    depth = 3 if lang == "ko" else 2
    up = "../" * depth
    over = r["kcal"] - TARGET_KCAL
    groups = "".join(
        '<div class="group">' + (f'<div class="label">{e(g["name"])}</div>' if g["name"] else "") + "<ul>"
        + "".join(f'<li><label><input type="checkbox"><span>{e(it)}</span></label></li>' for it in g["items"])
        + "</ul></div>" for g in c["groups"])
    steps = "".join(f"<li><span>{e(s)}</span></li>" for s in c["steps"])
    note_items = "".join(f"<li>{e(n)}</li>" for n in c["notes"])
    if c["source"]:
        note_items += "<li>" + (f'<a href="{e(c["source_url"])}" rel="noopener">{e(c["source"])}</a>' if c["source_url"] else e(c["source"])) + "</li>"
    notes = f'<section class="notes"><div class="label">{t["notes"]}</div><ul>{note_items}</ul></section>' if note_items else '<div style="height:40px"></div>'
    ld = {
        "@context": "https://schema.org", "@type": "Recipe", "name": c["title"], "description": c["desc"],
        "inLanguage": lang, "author": {"@type": "Person", "name": CFG.get("author", "")},
        "recipeYield": str(r["serves"]), "recipeCuisine": c["cuisine"],
        "recipeIngredient": [it for g in c["groups"] for it in g["items"]],
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in c["steps"]],
        "nutrition": {"@type": "NutritionInformation", "calories": f'{r["kcal"]} kcal',
                      "proteinContent": f'{r["protein"]} g', "fiberContent": f'{r["fiber"]} g'},
    }
    if r["date"]:
        ld["datePublished"] = r["date"]
    head = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>\n"
    hero_photo = f'\n    <div style="margin-bottom:36px">{picture(r, i, t, up, c["title"])}</div>' if r["photo"] else ""
    body = f"""    <a class="back" href="../../">{t['back']}</a>
    <section class="rhead">
      <div class="intro">
        <div class="label">{e(c['cuisine'])} · {t['serves'].format(n=r['serves'])}</div>
        <h1>{e(c['title'])}</h1>
        <p class="desc">{e(c['desc'])}</p>
      </div>
      <div class="facts">
        <div class="label">{t['per_serving_label']}</div>
        <div class="row">
          <div><div class="n">{r['kcal']}</div><div class="t">kcal</div></div>
          <div><div class="n">{r['protein']}<small> g</small></div><div class="t">{t['protein']}</div></div>
          <div><div class="n">{r['fiber']}<small> g</small></div><div class="t">{t['fiber']}</div></div>
        </div>
        <div class="verdict">{t['over'].format(n=over) if over > 0 else t['meets']}</div>
      </div>
    </section>{hero_photo}
    <section class="cols">
      <div><h2>{t['ingredients']}</h2>{groups}</div>
      <div><h2>{t['method']}</h2><ol class="steps">{steps}</ol></div>
    </section>
    {notes}"""
    return page(lang, depth, f"recipes/{r['slug']}/", f"ko/recipes/{r['slug']}/", c["title"], c["desc"], body, "recipes", head)


def about(lang):
    t = T[lang]
    services = "".join(f"<div><b>{s}</b><span>{t['example']}</span></div>" for s in t["services"])
    body = f"""    <section class="about">
      <div class="portrait"><span class="label">{t['your_photo']}</span></div>
      <div class="text">
        <h1>{t['about_title']}</h1>
        <p class="draft">{t['draft']}</p>
        <p class="lead">{t['about_lead']}</p>
        <p>{t['about_body']}</p>
        <div class="services">{services}</div>
      </div>
    </section>"""
    return page(lang, 2 if lang == "ko" else 1, "about/", "ko/about/", t["about_title"], t["about_lead"], body, "about")


def write(rel, text):
    p = DIST / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def main():
    recipes = load()
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    for lang, base in (("en", ""), ("ko", "ko/")):
        write(base + "index.html", home(lang, recipes))
        write(base + "about/index.html", about(lang))
        for i, r in enumerate(recipes):
            write(f"{base}recipes/{r['slug']}/index.html", recipe_page(lang, r, i))
    write(".nojekyll", "")
    print(f"Built {len(recipes)} recipes in 2 languages -> {DIST}")


if __name__ == "__main__":
    main()
