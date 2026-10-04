from flask import Flask, render_template

app = Flask(__name__)


# =========================
# ACTING WORKS
# =========================

works = [
    {
        "year": "2020",
        "type": "Series",
        "title": "I Told Sunset About You",
        "detail": "Billkin played Teh in the coming-of-age series set in Phuket.",
        "image": "images/itoldsunset.jpeg"
    },
    {
        "year": "2021",
        "type": "Series",
        "title": "I Promised You the Moon",
        "detail": "Billkin returned as Teh in the continuation of the story.",
        "image": "images/ipromisedu.jpeg"
    },
    {
        "year": "2024",
        "type": "Film",
        "title": "How to Make Millions Before Grandma Dies",
        "detail": "Billkin starred as M in the family drama film.",
        "image": "images/grandma.png"
    },
    {
        "year": "2025",
        "type": "Film",
        "title": "The Red Envelope",
        "detail": "Billkin played Menn in the supernatural comedy-drama.",
        "image": "images/red_envelope.jpg"
    }
]


# =========================
# ALBUMS / EPs
# =========================

albums = [
    {
        "year": "2023",
        "type": "EP",
        "title": "LOVE'S APPRENTICE",
        "image": "images/loves_apprentice.jpeg",
        "songs": [
            "ชอบตัวเองตอนอยู่กับเธอ (I Like Us)",
            "การเดินทางที่สวยงาม (A Beautiful Ride)",
            "Mr. Everything",
            "กลับมาคบกันเถอะ (Please Please)",
            "ยิ้มทั้งน้ำตา"
        ]
    },

    {
        "year": "2025",
        "type": "OST EP",
        "title": "ซองแดงแต่งผี (OST. The Red Envelope Album)",
        "image": "images/red_envelope_ost.jpeg",
        "songs": [
            "สัมภเวซี้ (GFF Ghost Friend Forever)",
            "ตื่น (Wake Up Call)",
            "ใจหล่น (Ruined)",
            "รักแรกพบ (Knock Knock)",
            "See You Somewhere"
        ]
    },

    {
        "year": "2025",
        "type": "Album",
        "title": "Grow With The Flow",
        "image": "images/grow_with_the_flow.jpeg",
        "songs": [
            "Daily Magic",
            "ก้าวก่าย (Still On Your Line)",
            "Golden Hour",
            "ยิ่งดุยิ่งชอบ (Bossy Baby)",
            "ตัวโดน (Always Me)",
            "นับหนึ่ง (From now on)",
            "ใครจะรู้ (Silent Blue)",
            "Grow With The Flow"
        ]
    },

    {
        "year": "2026",
        "type": "Album",
        "title": "BILLKIN FEELQUENCY",
        "image": "images/feelfrequency.jpeg",
        "songs": [
            "Mr. Everything",
            "รักแรกพบ (Knock Knock)",
            "ชอบตัวเองตอนอยู่กับเธอ (I Like Us)",
            "นับหนึ่ง (From now on)",
            "See You Somewhere",
            "ยิ้มทั้งน้ำตา",
            "Grow With The Flow",
            "Daily Magic",
            "ใครจะรู้ (Silent Blue)",
            "แปลไม่ออก (Untold Answer)",
            "ตัวโดน (Always Me)",
            "ก้าวก่าย (Still On Your Line)",
            "การเดินทางที่สวยงาม (A Beautiful Ride)",
            "กอดในใจ",
            "โคตรพิเศษ",
            "ยิ่งดุยิ่งชอบ (Bossy Baby)",
            "I ไม่ O (IXO)",
            "กลับมาคบกันเถอะ (Please Please)",
            "You Are My Everything",
            "กีดกัน (Skyline)"
        ]
    },

    {
        "year": "2026",
        "type": "Live Session",
        "title": "BILLKIN FEELQUENCY LIVE SESSION",
        "image": "images/feelfrequency_live_session.jpeg",
        "songs": [
            "Mr. Everything (FEELQUENCY LIVE SESSION)",
            "ชอบตัวเองตอนอยู่กับเธอ (I Like Us) [FEELQUENCY LIVE SESSION]",
            "ใครจะรู้ (Silent Blue) [FEELQUENCY LIVE SESSION]"
        ]
    }
]


# =========================
# ALL SONGS
# =========================

music = [
    {
        "year": "2017",
        "title": "ไม่กลัว (Mai Glua)",
        "note": "OST / Collaboration"
    },

    {
        "year": "2019",
        "title": "You Are My Everything",
        "note": "OST My Ambulance"
    },
    {
        "year": "2019",
        "title": "I Love You ต่อจากนี้จะขอรัก...รักเธอต่อไป",
        "note": "OST My Ambulance"
    },

    {
        "year": "2020",
        "title": "กอดในใจ (Hug in Mind)",
        "note": "with JAYLERR"
    },
    {
        "year": "2020",
        "title": "กีดกัน (Skyline)",
        "note": "OST I Told Sunset About You"
    },
    {
        "year": "2020",
        "title": "แปลไม่ออก (Untold Answer)",
        "note": "OST I Told Sunset About You"
    },
    {
        "year": "2020",
        "title": "โคตรพิเศษ",
        "note": "OST I Told Sunset About You"
    },

    {
        "year": "2021",
        "title": "หลอกกันทั้งนั้น (Fake News)",
        "note": "OST I Promised You the Moon"
    },
    {
        "year": "2021",
        "title": "I ไม่ O (IXO)",
        "note": "Single"
    },
    {
        "year": "2021",
        "title": "เก็บไว้ตลอดไป (Once & Forever)",
        "note": "Single"
    },
    {
        "year": "2021",
        "title": "รู้งี้เป็นแฟนกันตั้งนานแล้ว (Safe Zone)",
        "note": "with PP KRIT"
    },
    {
        "year": "2021",
        "title": "ทะเลสีดำ (The Black Sea)",
        "note": "with PP KRIT"
    },
    {
        "year": "2021",
        "title": "ไม่ปล่อยมือ (Coming of Age)",
        "note": "with PP KRIT"
    },
    {
        "year": "2021",
        "title": "คิดไม่ออก",
        "note": "with TangBadVoice"
    },
    {
        "year": "2021",
        "title": "มันดีเลย",
        "note": "Collaboration"
    },
    {
        "year": "2021",
        "title": "ลบไม่ได้ช่วยให้ลืม (LIVE SESSION)",
        "note": "with Ink Waruntorn"
    },

    {
        "year": "2022",
        "title": "ชอบตัวเองตอนอยู่กับเธอ (I Like Us)",
        "note": "LOVE'S APPRENTICE"
    },
    {
        "year": "2022",
        "title": "กลับมาคบกันเถอะ (Please Please)",
        "note": "LOVE'S APPRENTICE"
    },
    {
        "year": "2022",
        "title": "Mr. Everything",
        "note": "LOVE'S APPRENTICE"
    },
    {
        "year": "2022",
        "title": "Give Me Your Forever",
        "note": "with Zack Tabudlo"
    },
    {
        "year": "2022",
        "title": "แลกเลยปะ (Hoo Whee Hoo)",
        "note": "with PP KRIT and 4EVE"
    },
    {
        "year": "2022",
        "title": "Self Love",
        "note": "Collaboration"
    },

    {
        "year": "2023",
        "title": "ยิ้มทั้งน้ำตา",
        "note": "LOVE'S APPRENTICE"
    },
    {
        "year": "2023",
        "title": "การเดินทางที่สวยงาม (A Beautiful Ride)",
        "note": "LOVE'S APPRENTICE"
    },
    {
        "year": "2023",
        "title": "Daily Magic",
        "note": "Grow With The Flow"
    },
    {
        "year": "2023",
        "title": "กันและกัน",
        "note": "with Zom Marie"
    },

    {
        "year": "2024",
        "title": "ก้าวก่าย (Still On Your Line)",
        "note": "Grow With The Flow"
    },
    {
        "year": "2024",
        "title": "สวยงามเสมอ (Ever-Forever)",
        "note": "OST How to Make Millions Before Grandma Dies"
    },
    {
        "year": "2024",
        "title": "Golden Hour",
        "note": "Grow With The Flow"
    },
    {
        "year": "2024",
        "title": "ยิ่งดุยิ่งชอบ (Bossy Baby)",
        "note": "Grow With The Flow"
    },
    {
        "year": "2024",
        "title": "ยอม (Surrender)",
        "note": "with PP KRIT"
    },

    {
        "year": "2025",
        "title": "ตัวโดน (Always Me)",
        "note": "Grow With The Flow"
    },
    {
        "year": "2025",
        "title": "สัมภเวซี้ (GFF Ghost Friend Forever)",
        "note": "with PP KRIT"
    },
    {
        "year": "2025",
        "title": "รักแรกพบ (Knock Knock)",
        "note": "OST The Red Envelope"
    },
    {
        "year": "2025",
        "title": "See You Somewhere",
        "note": "OST The Red Envelope"
    },
    {
        "year": "2025",
        "title": "I'm OK // Not OK",
        "note": "with BOYdPOD"
    },
    {
        "year": "2025",
        "title": "I'm OK // Not OK (Headphones Version)",
        "note": "with BOYdPOD"
    },
    {
        "year": "2025",
        "title": "Oh It's You",
        "note": "Collaboration"
    },
    {
        "year": "2025",
        "title": "ขอโทษได้ไหม (If Only)",
        "note": "with NONT TANONT"
    },
    {
        "year": "2025",
        "title": "นับหนึ่ง (From now on)",
        "note": "Grow With The Flow"
    },
    {
        "year": "2025",
        "title": "นับหนึ่ง (From now on) - Instrumental",
        "note": "Instrumental"
    },
    {
        "year": "2025",
        "title": "ใครจะรู้ (Silent Blue)",
        "note": "Grow With The Flow"
    },
    {
        "year": "2025",
        "title": "Grow With The Flow",
        "note": "Album title track"
    },

    {
        "year": "2026",
        "title": "Mr. Everything (FEELQUENCY LIVE SESSION)",
        "note": "Live Session"
    },
    {
        "year": "2026",
        "title": "ชอบตัวเองตอนอยู่กับเธอ (I Like Us) [FEELQUENCY LIVE SESSION]",
        "note": "Live Session"
    },
    {
        "year": "2026",
        "title": "ใครจะรู้ (Silent Blue) [FEELQUENCY LIVE SESSION]",
        "note": "Live Session"
    },
    {
        "year": "2026",
        "title": "ไม่มีวันไหนที่ไม่คิดถึง (starlost.) [Side by Side Session]",
        "note": "with PURPEECH"
    },
    {
        "year": "2026",
        "title": "See You Somewhere (LIVE SESSION)",
        "note": "with PURPEECH"
    },
    {
        "year": "2026",
        "title": "ผลข้างเคียง (Love Effects)",
        "note": "with Ink Waruntorn"
    },
    {
        "year": "2026",
        "title": "CHECKLIST",
        "note": "Single"
    }
]


@app.route("/")
def home():
    return render_template(
        "index.html",
        works=works,
        music=music,
        albums=albums
    )


if __name__ == "__main__":
    app.run(debug=True)