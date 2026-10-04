"""Builds the Billkin fan site into ./docs (served by GitHub Pages).

Run:  python build.py
Edit the MUSIC and SCREEN lists below to change the content.
"""
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "docs"

# ---- Content (edit freely; add years/links once you've verified them) ----
MUSIC = [
    ("Feelquency", "img/feelquency.jpeg", "Album art: Billkin among a city built from piano keys and brass pipes."),
    ("Feelquency Live Session", "img/feelquency-live.jpeg", "A live, stripped-back take on the Feelquency songs."),
    ("Grow with the Flow", "img/grow-with-the-flow.jpeg", "Single art: a run along a lake at sunset."),
    ("Love's Apprentice", "img/loves-apprentice.jpeg", "Single art: a quiet look through a car window, flowers in hand."),
    ("The Red Envelope (OST)", "img/red-envelope-ost.jpeg", "Soundtrack single with PP Krit for the film The Red Envelope."),
]

SCREEN = [
    ("How to Make Millions Before Grandma Dies", "Film · 2024",
     "img/grandma.png", "A film about a grandson, his grandmother and the family around them."),
    ("I Told Sunset About You", "Series · 2020",
     "img/i-told-sunset.jpeg", "Billkin and PP Krit's first on-screen pairing."),
    ("I Promised You the Moon", "Series",
     "img/i-promised-you.jpeg", "Billkin and PP Krit reunite on screen."),
    ("The Red Envelope", "Film",
     "img/red-envelope.jpg", "Billkin and PP Krit in a film with its own soundtrack single."),
]
# --------------------------------------------------------------------------

def music_html():
    return "\n".join(
        f'<figure class="rec"><img src="{src}" alt="{escape(t)} cover art" loading="lazy">'
        f"<figcaption><h3>{escape(t)}</h3><p>{escape(d)}</p></figcaption></figure>"
        for t, src, d in MUSIC
    )

def screen_html():
    return "\n".join(
        f'<article class="work"><img src="{src}" alt="Still from {escape(t)}" loading="lazy">'
        f"<div><h3>{escape(t)}</h3><p class='meta'>{escape(m)}</p><p>{escape(d)}</p></div></article>"
        for t, m, src, d in SCREEN
    )

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Billkin: music and screen work</title>
<meta name="description" content="A fan-made guide to Billkin's albums, singles, films and series.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,800&family=Instrument+Sans:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="hero">
  <img src="img/studio.jpg" alt="Billkin wearing headphones in a recording studio">
  <div class="hero-text">
    <h1>Billkin</h1>
    <p>Singer and actor. This page collects his albums, singles, films and series.</p>
    <nav><a href="#music">Music</a><a href="#screen">Film and series</a></nav>
  </div>
</header>
<main>
  <section id="music">
    <h2>Music</h2>
    <div class="records">
%%MUSIC%%
    </div>
  </section>
  <section id="screen">
    <h2>Film and series</h2>
%%SCREEN%%
  </section>
</main>
<footer>
  <p>Fan-made site, not affiliated with Billkin or his management. Images belong to their respective owners.</p>
</footer>
</body>
</html>
"""

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "src" / "img", OUT / "img")
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    html = PAGE.replace("%%MUSIC%%", music_html()).replace("%%SCREEN%%", screen_html())
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print(f"Built {OUT / 'index.html'}")

if __name__ == "__main__":
    main()
