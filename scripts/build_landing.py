#!/usr/bin/env python3
"""Build the GitHub Pages site (docs/) from the canonical markdown.

Renders the essay and the About page into self-contained, dependency-free
editorial HTML that shares one nav, stylesheet, and theme toggle. The essay
markdown stays the single source of truth. Re-run after editing either file:

    python scripts/build_landing.py

GitHub Pages serves the `docs/` folder: docs/index.html is the home (the essay),
docs/about.html is "How this was made", docs/demo/ is the interactive demo.

Note: docs/demo/index.html is the site-integrated demo (shared nav, shared
light/dark theme, English default) and is maintained by hand — do NOT overwrite it
by copying demo/blind_dimension.html, which is kept as the pristine extracted
artifact. This script does not touch docs/demo/.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
REPO = "https://github.com/Kirill-Kruglov/proxylimen"


def pandoc(md_path):
    return subprocess.run(
        ["pandoc", str(md_path), "-t", "html", "--no-highlight"],
        capture_output=True, text=True, check=True,
    ).stdout


def toc_from(body):
    heads = re.findall(r'<h([12]) id="([^"]+)">(.*?)</h[12]>', body, re.DOTALL)
    items, first_h1 = [], False
    for level, hid, text in heads:
        text = re.sub(r"<[^>]+>", "", text).strip()
        if level == "1" and not first_h1:
            first_h1 = True
            continue
        cls = "toc-h1" if level == "1" else "toc-h2"
        items.append(f'<a class="{cls}" href="#{hid}">{text}</a>')
    return "\n".join(items)


CSS = """
:root{--bg:#fbfaf6;--ink:#1d1c1a;--muted:#6b6760;--line:#e4e0d6;--accent:#7a5b2e;--rule:#ece8de;--tablehead:#f3f0e8;--quote-bg:#f1ead9}
:root[data-theme=dark]{--bg:#15171c;--ink:#dfdcd4;--muted:#9a958c;--line:#2a2d34;--accent:#cdb079;--rule:#23262d;--tablehead:#1c1f25;--quote-bg:#1e222a}
@media (prefers-color-scheme:dark){:root:not([data-theme]){--bg:#15171c;--ink:#dfdcd4;--muted:#9a958c;--line:#2a2d34;--accent:#cdb079;--rule:#23262d;--tablehead:#1c1f25;--quote-bg:#1e222a}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:20px/1.7 Iowan Old Style,Palatino,Georgia,"Times New Roman",serif;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
.nav{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;align-items:center;
  gap:16px;padding:12px clamp(16px,5vw,40px);background:var(--bg);border-bottom:1px solid var(--line);
  font-family:system-ui,-apple-system,Segoe UI,sans-serif;font-size:15px}
.nav .brand{font-weight:700;letter-spacing:.02em;color:var(--ink);text-decoration:none}
.nav .right{display:flex;align-items:center;gap:18px}
.nav a{color:var(--muted);text-decoration:none}
.nav a:hover{color:var(--ink)}
.nav button{background:none;border:1px solid var(--line);color:var(--muted);border-radius:999px;
  width:34px;height:34px;cursor:pointer;font-size:15px;line-height:1}
.nav button:hover{color:var(--ink)}
main{max-width:680px;margin:0 auto;padding:0 22px 96px}
.byline{margin:18px 0 0;font-family:system-ui,sans-serif;font-size:14px;color:var(--muted)}
.byline a{color:var(--muted);text-decoration:underline;text-underline-offset:2px}
.byline a:hover{color:var(--ink)}
h1{font-size:clamp(34px,6vw,52px);line-height:1.08;letter-spacing:-.01em;margin:48px 0 8px}
h2{font-size:26px;line-height:1.2;margin:52px 0 6px}
h3{font-size:20px;line-height:1.25;margin:32px 0 4px;color:var(--muted);font-weight:600}
p{margin:0 0 20px}
a{color:var(--accent);text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:.5px}
strong{font-weight:700}
hr{border:0;border-top:1px solid var(--rule);margin:44px 0}
blockquote{margin:30px 0;padding:14px 22px;border-left:3px solid var(--accent);
  background:var(--quote-bg);border-radius:0 8px 8px 0;color:var(--ink);font-size:20px;font-style:italic}
blockquote p{margin:0 0 10px}
blockquote p:last-child{margin:0}
table{width:100%;border-collapse:collapse;margin:24px 0;font-size:15.5px;font-family:system-ui,sans-serif}
th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line)}
thead th{background:var(--tablehead);border-bottom:2px solid var(--line);font-weight:600}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.86em;
  background:color-mix(in srgb,var(--ink) 7%,transparent);padding:.1em .35em;border-radius:4px}
.contents{margin:34px 0 8px;border:1px solid var(--line);border-radius:10px;
  font-family:system-ui,sans-serif;font-size:15px}
.contents summary{cursor:pointer;padding:5px 18px;color:var(--muted);font-weight:600;list-style:none}
.contents summary::-webkit-details-marker{display:none}
.contents summary::before{content:"\\203A";display:inline-block;padding-right:7px;transition:transform .15s}
.contents[open] summary::before{transform:rotate(90deg)}
.contents nav{display:flex;flex-direction:column;padding:0 16px 14px}
.contents a{color:var(--muted);text-decoration:none;padding:4px 0}
.contents a:hover{color:var(--ink)}
.contents .toc-h1{color:var(--ink);font-weight:700;margin-top:10px}
.contents .toc-h2{padding-left:16px}
footer{max-width:680px;margin:0 auto;padding:28px 22px 64px;border-top:1px solid var(--rule);
  color:var(--muted);font-family:system-ui,sans-serif;font-size:14px}
footer a{color:var(--muted)}
"""

NAV = """<nav class="nav">
  <a class="brand" href="./">proxylimen</a>
  <div class="right">
    <a href="./">Essay</a>
    <a href="demo/">Demo</a>
    <a href="about.html">About</a>
    <a href="REPO">GitHub</a>
    <button id="theme" type="button" aria-label="Toggle light / dark">&#9682;</button>
  </div>
</nav>""".replace("REPO", REPO)

THEME_JS = """<script>
(function(){
  var root=document.documentElement, KEY="proxylimen-theme";
  var saved=localStorage.getItem(KEY);
  if(saved) root.setAttribute("data-theme",saved);
  document.getElementById("theme").addEventListener("click",function(){
    var cur=root.getAttribute("data-theme");
    if(!cur) cur=matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";
    var next=cur==="dark"?"light":"dark";
    root.setAttribute("data-theme",next);
    localStorage.setItem(KEY,next);
  });
})();
</script>"""

FOOTER = f"""<footer>
  <p><strong>proxylimen</strong> — essay, experiments, the self-checking gate
  harness, and the interactive demo:
  <a href="{REPO}">github.com/Kirill-Kruglov/proxylimen</a>.
  Written one step earlier in the chain than Dario Amodei's
  <a href="https://www.darioamodei.com/essay/machines-of-loving-grace">Machines of Loving Grace</a>
  and <em>The Adolescence of Technology</em>: before a machine acts on the world,
  where does the world inside it come from?</p>
</footer>"""

BYLINE = ('<p class="byline">By Kirill Kruglov, developed in dialogue with Codex, Claude, and Fable'
          ' — <a href="about.html">how this was made</a>.</p>')


def page(title, description, body, *, contents="", byline=""):
    head = (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{title}</title>\n"
        f'<meta name="description" content="{description}">\n'
        f'<meta property="og:title" content="{title}">\n'
        f'<meta property="og:description" content="{description}">\n'
        '<meta property="og:type" content="article">\n'
        f"<style>{CSS}</style>\n"
        '<script>try{var t=localStorage.getItem("proxylimen-theme");'
        'if(t)document.documentElement.setAttribute("data-theme",t);}catch(e){}</script>\n'
        "</head>\n<body>\n"
    )
    main = f'<main id="top">\n{byline}\n{contents}\n<article>\n{body}\n</article>\n</main>\n'
    return head + NAV + "\n" + main + FOOTER + "\n" + THEME_JS + "\n</body>\n</html>\n"


def main():
    DOCS.mkdir(exist_ok=True)
    essay = pandoc(ROOT / "essay" / "everything-from-almost-nothing.md")
    # the essay links the appendix by its repo-relative path; on the site it is a page
    essay = essay.replace("appendices/A-the-measured-boundary.md", "appendix-a.html")
    contents = (f'<details class="contents">\n<summary>Contents</summary>\n'
                f'<nav>\n{toc_from(essay)}\n</nav>\n</details>')
    (DOCS / "index.html").write_text(page(
        "Everything From Almost Nothing",
        "Can a world be derived without an oracle? Tiny worlds, an instrument built "
        "to catch the author cheating, and a precise map of when knowledge can be "
        "derived rather than inherited — one step earlier than Machines of Loving Grace.",
        essay, contents=contents, byline=BYLINE,
    ), encoding="utf-8")
    about = pandoc(ROOT / "essay" / "about.md")
    (DOCS / "about.html").write_text(page(
        "How this was made — proxylimen",
        "How proxylimen was built: one person in adversarial dialogue with Codex, "
        "Claude, and Fable, behind a harness that refuses to certify unprovenanced results.",
        about,
    ), encoding="utf-8")
    appendix = pandoc(ROOT / "essay" / "appendices" / "A-the-measured-boundary.md")
    # repo-relative links inside the appendix should point at GitHub, not the site
    appendix = re.sub(r'href="\.\./\.\./', f'href="{REPO}/blob/main/', appendix)
    (DOCS / "appendix-a.html").write_text(page(
        "Appendix A — The Measured Boundary",
        "Definitions, controls, crossover tables with confidence intervals, the "
        "fixed-k caveat, and the exact file behind every number in the essay.",
        appendix,
    ), encoding="utf-8")
    print(f"wrote {DOCS/'index.html'}, {DOCS/'about.html'}, {DOCS/'appendix-a.html'}")


if __name__ == "__main__":
    main()
