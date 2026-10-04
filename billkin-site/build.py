"""Builds the Billkin fan site into ./docs (GitHub Pages).  Run: python build.py
Edit the data below, change THEME ("sunset", "piano" or "studio"), then rebuild."""
import shutil
from html import escape as e
from pathlib import Path
from urllib.parse import quote

ROOT, OUT = Path(__file__).parent, Path(__file__).parent / "docs"
THEME = "sunset"

# (title, label, image, tracks separated by |)
ALBUMS = [
 ("LOVE'S APPRENTICE", "2023 EP", "loves-apprentice.jpeg",
  "ชอบตัวเองตอนอยู่กับเธอ (I Like Us)|การเดินทางที่สวยงาม (A Beautiful Ride)|Mr. Everything|กลับมาคบกันเถอะ (Please Please)|ยิ้มทั้งน้ำตา"),
 ("ซองแดงแต่งผี (OST. The Red Envelope Album)", "2025 OST EP", "red-envelope-ost.jpeg",
  "สัมภเวซี้ (GFF Ghost Friend Forever)|ตื่น (Wake Up Call)|ใจหล่น (Ruined)|รักแรกพบ (Knock Knock)|See You Somewhere"),
 ("Grow With The Flow", "2025 Album", "grow-with-the-flow.jpeg",
  "Daily Magic|ก้าวก่าย (Still On Your Line)|Golden Hour|ยิ่งดุยิ่งชอบ (Bossy Baby)|ตัวโดน (Always Me)|นับหนึ่ง (From now on)|ใครจะรู้ (Silent Blue)|Grow With The Flow"),
 ("BILLKIN FEELQUENCY", "2026 Album", "feelquency.jpeg",
  "Mr. Everything|รักแรกพบ (Knock Knock)|ชอบตัวเองตอนอยู่กับเธอ (I Like Us)|นับหนึ่ง (From now on)|See You Somewhere|ยิ้มทั้งน้ำตา|Grow With The Flow|Daily Magic|ใครจะรู้ (Silent Blue)|แปลไม่ออก (Untold Answer)|ตัวโดน (Always Me)|ก้าวก่าย (Still On Your Line)|การเดินทางที่สวยงาม (A Beautiful Ride)|กอดในใจ|โคตรพิเศษ|ยิ่งดุยิ่งชอบ (Bossy Baby)|I ไม่ O (IXO)|กลับมาคบกันเถอะ (Please Please)|You Are My Everything|กีดกัน (Skyline)"),
 ("BILLKIN FEELQUENCY LIVE SESSION", "2026 Live Session", "feelquency-live.jpeg",
  "Mr. Everything (FEELQUENCY LIVE SESSION)|ชอบตัวเองตอนอยู่กับเธอ (I Like Us) [FEELQUENCY LIVE SESSION]|ใครจะรู้ (Silent Blue) [FEELQUENCY LIVE SESSION]"),
]

# year | title | note
SONGS = """2017|ไม่กลัว (Mai Glua)|OST / Collaboration
2019|You Are My Everything|OST My Ambulance
2019|I Love You ต่อจากนี้จะขอรัก...รักเธอต่อไป|OST My Ambulance
2020|กอดในใจ (Hug in Mind)|with JAYLERR
2020|กีดกัน (Skyline)|OST I Told Sunset About You
2020|แปลไม่ออก (Untold Answer)|OST I Told Sunset About You
2020|โคตรพิเศษ|OST I Told Sunset About You
2021|หลอกกันทั้งนั้น (Fake News)|OST I Promised You the Moon
2021|I ไม่ O (IXO)|Single
2021|เก็บไว้ตลอดไป (Once & Forever)|Single
2021|รู้งี้เป็นแฟนกันตั้งนานแล้ว (Safe Zone)|with PP KRIT
2021|ทะเลสีดำ (The Black Sea)|with PP KRIT
2021|ไม่ปล่อยมือ (Coming of Age)|with PP KRIT
2021|คิดไม่ออก|with TangBadVoice
2021|มันดีเลย|Collaboration
2021|ลบไม่ได้ช่วยให้ลืม (LIVE SESSION)|with Ink Waruntorn
2022|ชอบตัวเองตอนอยู่กับเธอ (I Like Us)|LOVE'S APPRENTICE
2022|กลับมาคบกันเถอะ (Please Please)|LOVE'S APPRENTICE
2022|Mr. Everything|LOVE'S APPRENTICE
2022|Give Me Your Forever|with Zack Tabudlo
2022|แลกเลยปะ (Hoo Whee Hoo)|with PP KRIT and 4EVE
2022|Self Love|Collaboration
2023|ยิ้มทั้งน้ำตา|LOVE'S APPRENTICE
2023|การเดินทางที่สวยงาม (A Beautiful Ride)|LOVE'S APPRENTICE
2023|Daily Magic|Grow With The Flow
2023|กันและกัน|with Zom Marie
2024|ก้าวก่าย (Still On Your Line)|Grow With The Flow
2024|สวยงามเสมอ (Ever-Forever)|OST How to Make Millions Before Grandma Dies
2024|Golden Hour|Grow With The Flow
2024|ยิ่งดุยิ่งชอบ (Bossy Baby)|Grow With The Flow
2024|ยอม (Surrender)|with PP KRIT
2025|ตัวโดน (Always Me)|Grow With The Flow
2025|สัมภเวซี้ (GFF Ghost Friend Forever)|with PP KRIT
2025|รักแรกพบ (Knock Knock)|OST The Red Envelope
2025|See You Somewhere|OST The Red Envelope
2025|I'm OK // Not OK|with BOYdPOD
2025|I'm OK // Not OK (Headphones Version)|with BOYdPOD
2025|Oh It's You|Collaboration
2025|ขอโทษได้ไหม (If Only)|with NONT TANONT
2025|นับหนึ่ง (From now on)|Grow With The Flow
2025|นับหนึ่ง (From now on) - Instrumental|Instrumental
2025|ใครจะรู้ (Silent Blue)|Grow With The Flow
2025|Grow With The Flow|Album title track
2026|Mr. Everything (FEELQUENCY LIVE SESSION)|Live Session
2026|ชอบตัวเองตอนอยู่กับเธอ (I Like Us) [FEELQUENCY LIVE SESSION]|Live Session
2026|ใครจะรู้ (Silent Blue) [FEELQUENCY LIVE SESSION]|Live Session
2026|ไม่มีวันไหนที่ไม่คิดถึง (starlost.) [Side by Side Session]|with PURPEECH
2026|See You Somewhere (LIVE SESSION)|with PURPEECH
2026|ผลข้างเคียง (Love Effects)|with Ink Waruntorn
2026|CHECKLIST|Single"""

ACTING = [
 ("I Told Sunset About You", "2020 Series", "i-told-sunset.jpeg", "Billkin played Teh in the coming-of-age series set in Phuket."),
 ("I Promised You the Moon", "2021 Series", "i-promised-you.jpeg", "Billkin returned as Teh in the continuation of the story."),
 ("How to Make Millions Before Grandma Dies", "2024 Film", "grandma.png", "Billkin starred as M in the family drama film."),
 ("The Red Envelope", "2025 Film", "red-envelope.jpg", "Billkin played Menn in the supernatural comedy-drama."),
]

def albums():
    out = []
    for t, lab, img, tr in ALBUMS:
        items = "".join(f"<li>{e(x)}</li>" for x in tr.split("|"))
        out.append(f'<article class="album"><img src="img/{img}" alt="{e(t)} cover" loading="lazy">'
                   f'<div><p class="tag">{lab}</p><h3>{e(t)}</h3><details open><summary>Tracklist</summary><ol>{items}</ol></details></div></article>')
    return "\n".join(out)

def songs():
    rows = []
    for line in SONGS.splitlines():
        y, t, n = line.split("|")
        url = "https://open.spotify.com/search/" + quote("Billkin " + t)
        rows.append(f'<li><span class="yr">{y}</span><span class="st">{e(t)}</span><span class="sn">{e(n)}</span>'
                    f'<a href="{url}" target="_blank" rel="noopener" aria-label="Search {e(t)} on Spotify">↗</a></li>')
    return "\n".join(rows)

def acting():
    return "\n".join(
        f'<article class="work"><img src="img/{i}" alt="Still from {e(t)}" loading="lazy">'
        f'<p class="tag">{lab}</p><h3>{e(t)}</h3><p>{e(d)}</p></article>' for t, lab, i, d in ACTING)

PAGE = """<!doctype html>
<html lang="en" data-theme="%%THEME%%">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Billkin | Works</title>
<meta name="description" content="Fan-made collection of Billkin's albums, songs and acting works.">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;800&family=Figtree:wght@400;500&family=Noto+Sans+Thai:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="bar">
  <a class="logo" href="#home">BILLKIN.</a>
  <nav><a href="#about">About</a><a href="#albums">Albums</a><a href="#music">Songs</a><a href="#acting">Acting</a></nav>
  <div class="themes" role="group" aria-label="Theme">
    <button data-set="sunset">Sunset</button><button data-set="piano">Piano</button><button data-set="studio">Studio</button>
  </div>
</header>
<section id="home" class="hero">
  <div>
    <p class="tag">Actor · Singer · Artist</p>
    <h1>Billkin <span>Putthipong</span></h1>
    <p class="lead">A fan-made collection of Billkin Putthipong's music, albums, songs and acting works.</p>
    <a class="btn" href="#albums">Explore his work ↓</a>
  </div>
  <img src="img/studio.jpg" alt="Billkin Putthipong in a recording studio">
</section>
<main>
<section id="about" class="about">
  <p class="num">01</p>
  <div><p class="tag">About</p><h2>From screen stories to music.</h2></div>
  <div class="copy"><p>Billkin is a Thai actor and recording artist known for his acting, pop music and soundtrack releases.</p>
  <p>This website presents his albums, songs and selected acting works.</p></div>
</section>
<section id="albums"><p class="num">02</p><p class="tag">Discography</p><h2>Albums &amp; EPs</h2>
%%ALBUMS%%
</section>
<section id="music"><p class="num">03</p><p class="tag">Complete discography</p><h2>All Songs</h2>
<ul class="songs">
%%SONGS%%
</ul></section>
<section id="acting"><p class="num">04</p><p class="tag">Acting</p><h2>On Screen</h2>
<div class="works">
%%ACTING%%
</div></section>
</main>
<footer>
  <h2>Where stories meet. Music lives.</h2>
  <p>Fan-made site, not affiliated with Billkin or his management. Images belong to their owners.</p>
</footer>
<script>
document.querySelectorAll("[data-set]").forEach(function(b){
  b.addEventListener("click",function(){
    document.documentElement.dataset.theme=b.dataset.set;
    try{localStorage.setItem("theme",b.dataset.set)}catch(x){}
  });
});
try{var t=localStorage.getItem("theme");if(t)document.documentElement.dataset.theme=t}catch(x){}
</script>
</body>
</html>
"""

def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir()
    shutil.copytree(ROOT / "src" / "img", OUT / "img")
    shutil.copy(ROOT / "src" / "style.css", OUT / "style.css")
    html = (PAGE.replace("%%THEME%%", THEME).replace("%%ALBUMS%%", albums())
            .replace("%%SONGS%%", songs()).replace("%%ACTING%%", acting()))
    (OUT / "index.html").write_text(html, encoding="utf-8")
    print("Built", OUT / "index.html")

if __name__ == "__main__":
    main()
