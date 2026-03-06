#!/usr/bin/env python3
"""
build.py — Generate static HTML pages for Cornelius à Lapide's Biblical Commentary
Output: /Users/master/.openclaw/workspace/projects/website/lapide/

Structure:
  lapide/index.html             — master book list
  lapide/{book}/index.html      — chapter list for a book
  lapide/{book}/{chapter}.html  — commentary for one chapter
"""

import csv
import html
import os
import re
import shutil
from collections import defaultdict, OrderedDict
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR
DRB_DIR = Path("/Users/master/.openclaw/workspace/projects/drb")

# ─── Book metadata ─────────────────────────────────────────────────────────────
# (tsv_key, html_filename, display_name, canon_group, author, intro)
BOOK_META = [
    # OLD TESTAMENT
    ("Gn",    "genesis",          "Genesis",                   "OT", "à Lapide",
     "Cornelius à Lapide opens his commentary on Genesis with extraordinary breadth, tracing creation through the lens of the Fathers and scholastics, illuminating the literal, allegorical, and moral senses of each verse from the first day through the Patriarchs."),
    ("Ex",    "exodus",           "Exodus",                    "OT", "à Lapide",
     "In Exodus, à Lapide expounds the great acts of God's deliverance — the plagues, the Passover, the crossing of the Red Sea, and the giving of the Law — drawing heavily on SS. Augustine, Jerome, and Thomas to reveal their Christological and ecclesiological depth."),
    ("Lv",    "leviticus",        "Leviticus",                 "OT", "à Lapide",
     "À Lapide's Leviticus commentary treats the sacrificial law as a treasury of types and figures, each rite and ceremony pointing forward to the one perfect sacrifice of Christ and the sacramental economy of the Church."),
    ("Nm",    "numbers",          "Numbers",                   "OT", "à Lapide",
     "In Numbers, à Lapide follows Israel through the wilderness, interpreting the journeys, murmurings, and divine ordinances as figures of the soul's pilgrimage toward God and the life of grace."),
    ("Dt",    "deuteronomy",      "Deuteronomy",               "OT", "à Lapide",
     "À Lapide's commentary on Deuteronomy dwells on Moses' great discourses as a compendium of the moral law, drawing out obligations of justice, mercy, and fidelity that apply to all ages and states of life."),
    ("Jos",   "joshua",           "Joshua",                    "OT", "à Lapide",
     "The Book of Joshua is read by à Lapide as the conquest of the Promised Land typifying the warfare of the Christian soul against sin and the entry into heavenly rest, with Joshua himself a figure of Jesus."),
    ("Jgs",   "judges",           "Judges",                    "OT", "à Lapide",
     "À Lapide's Judges commentary explores the cycles of apostasy and deliverance, finding in the judges themselves — Gideon, Samson, Deborah — rich types of Christ the liberator and the Church's perennial struggle with infidelity."),
    ("Ru",    "ruth",             "Ruth",                      "OT", "à Lapide",
     "In Ruth, à Lapide finds a model of fidelity, humility, and charity, expounding Boaz and Ruth as figures of Christ and the Church, and their union as a type of the mystical marriage."),
    ("1Sam",  "1samuel",          "1 Samuel",                  "OT", "à Lapide",
     "À Lapide's commentary on 1 Samuel traces Samuel's prophetic vocation, Saul's tragic reign, and David's rise, drawing out lessons on obedience, the nature of kingship, and the providential preparation for Christ's royal lineage."),
    ("2Sam",  "2samuel",          "2 Samuel",                  "OT", "à Lapide",
     "In 2 Samuel, à Lapide expounds the full scope of David's reign — his triumphs, his grave sin, his penance, and his poetic spirit — as a compendium of the moral and spiritual life."),
    ("1Kings","1kings",           "1 Kings",                   "OT", "à Lapide",
     "À Lapide's 1 Kings commentary dwells on the splendour and eventual fall of Solomon's kingdom, the schism of Israel, and Elijah's prophetic mission, treating the Temple as the pre-eminent type of the Church."),
    ("2Kings","2kings",           "2 Kings",                   "OT", "à Lapide",
     "In 2 Kings, à Lapide traces the decline and captivity of both kingdoms, expounding Elisha's miracles as figures of the sacraments and the divine mercy that persists even in judgment."),
    ("1Chr",  "1chronicles",      "1 Chronicles",              "OT", "à Lapide",
     "À Lapide's Chronicles commentary treats the genealogies and temple preparations as a theologically charged account of God's covenant faithfulness, drawing on their spiritual resonances with the New Testament."),
    ("2Chr",  "2chronicles",      "2 Chronicles",              "OT", "à Lapide",
     "In 2 Chronicles, à Lapide follows the history of Judah's kings from Solomon to the exile, reading the narrative as a sustained meditation on fidelity to the covenant and the consequences of apostasy."),
    ("Ezr",   "ezra",             "Ezra",                      "OT", "à Lapide",
     "À Lapide's Ezra commentary expounds the return from exile and the rebuilding of the Temple as a type of the soul's return to God through penance and the restoration of divine worship."),
    ("Neh",   "nehemiah",         "Nehemiah",                  "OT", "à Lapide",
     "In Nehemiah, à Lapide reads the rebuilding of Jerusalem's walls as a figure of the Church's defence of doctrine and discipline, and Nehemiah himself as a model of zealous pastoral leadership."),
    ("Tb",    "tobit",            "Tobit",                     "OT", "à Lapide",
     "À Lapide's Tobit commentary is a sustained meditation on providence, prayer, and almsgiving, finding in Tobias's journey a type of the Christian life guided by the angelic ministry of the Church."),
    ("Jdt",   "judith",           "Judith",                    "OT", "à Lapide",
     "In Judith, à Lapide finds a pre-eminent figure of the Blessed Virgin Mary crushing the head of the enemy, and expounds Judith's faith and courage as models for the Church militant."),
    ("Est",   "esther",           "Esther",                    "OT", "à Lapide",
     "À Lapide's Esther commentary reads the deliverance of the Jewish people as a type of Mary's intercession and the Church's triumph over her persecutors, Esther herself being the Virgin's most illustrious prefiguration."),
    ("1Mc",   "1maccabees",       "1 Maccabees",               "OT", "à Lapide",
     "In 1 Maccabees, à Lapide expounds the Hasmonean revolt as a model of armed defence of divine worship, drawing lessons on the just war, the courage of martyrs, and the indefectibility of God's covenant."),
    ("2Mc",   "2maccabees",       "2 Maccabees",               "OT", "à Lapide",
     "À Lapide's 2 Maccabees commentary dwells especially on the theology of martyrdom, purgatory, and prayer for the dead, finding in Judas Maccabeus's offering for the fallen (2 Macc 12:43) a clear Scriptural ground for Catholic doctrine."),
    ("Prv",   "proverbs",         "Proverbs",                  "OT", "à Lapide",
     "In Proverbs, à Lapide offers an encyclopedic moral commentary, expounding Solomon's maxims through Aristotle, the Fathers, and the scholastics, treating Lady Wisdom as a figure of Christ and the Church."),
    ("Eccl",  "ecclesiastes",     "Ecclesiastes",              "OT", "à Lapide",
     "À Lapide's Ecclesiastes commentary reads Solomon's reflections on vanity as a sustained call to the contemptus mundi, expounding each verse through the lenses of ascetical theology and patristic allegory."),
    ("Sg",    "songofsongscanticle", "Song of Songs",           "OT", "à Lapide",
     "In the Song of Songs, à Lapide follows the Alexandrian tradition of reading the canticle as a dialogue between Christ and the Church (or the soul), drawing on Origen, Bernard, and the entire mystical tradition."),
    ("Wis",   "wisdom",           "Wisdom",                    "OT", "à Lapide",
     "À Lapide's Wisdom commentary treats the book as a summit of Old Testament theology, expounding the divine attributes, the immortality of the soul, and the condemnation of idolatry through an immense patristic synthesis."),
    ("Sir",   "sirach",           "Sirach (Ecclesiasticus)",   "OT", "à Lapide",
     "In Sirach, à Lapide provides one of his most practically detailed commentaries, expounding the sage's moral counsels on friendship, humility, speech, and the fear of God with characteristic thoroughness."),
    ("Is",    "isaiah",           "Isaiah",                    "OT", "à Lapide",
     "À Lapide's Isaiah commentary is among his most celebrated, expounding the great Messianic prophecies — the Immanuel oracle, the Servant Songs, the Suffering Servant of chapter 53 — as directly prophetic of Christ."),
    ("Jer",   "jeremiah",         "Jeremiah",                  "OT", "à Lapide",
     "In Jeremiah, à Lapide traces the weeping prophet's oracles of judgment and hope, reading the New Covenant promise of chapter 31 as the clearest Old Testament anticipation of the Eucharist and the Church."),
    ("Lam",   "lamentations",     "Lamentations",              "OT", "à Lapide",
     "À Lapide's Lamentations commentary reads Jeremiah's elegies over ruined Jerusalem as a figure of the soul's sorrow for sin and as a type of Our Lord's Passion, drawing on the Fathers' deep identification of Zion with the Church."),
    ("Bar",   "baruch",           "Baruch",                    "OT", "à Lapide",
     "In Baruch, à Lapide expounds the exilic prayer and wisdom hymn as a compendium of penitential theology, finding in chapter 3's praise of Wisdom a direct Christological prophecy."),
    ("Ez",    "ezekiel",          "Ezekiel",                   "OT", "à Lapide",
     "À Lapide's Ezekiel commentary is a monument of allegorical exegesis, treating the four living creatures, the dry bones, and the visionary temple as inexhaustible figures of Christ, the Church, and the Last Things."),
    ("Dn",    "daniel",           "Daniel",                    "OT", "à Lapide",
     "In Daniel, à Lapide expounds the four monarchies, the Son of Man vision, and the seventy weeks with great precision, treating the book as the most prophetically exact anticipation of Christ's coming in the entire Old Testament."),
    # Job — Corderius
    ("Jb",    "job",              "Job",                       "OT", "Corderius",
     "The commentary on Job is the work of <strong>Balthasar Corderius SJ</strong> (1592–1650), not à Lapide — a fellow Jesuit whose learned catena on Job draws on the Greek Fathers, Chrysostom, and Gregory's <em>Moralia</em> in exhaustive detail."),
    # NEW TESTAMENT
    ("Mt",    "matthew",          "Matthew",                   "NT", "à Lapide",
     "À Lapide's Matthew is among his earliest and most influential commentaries, expounding the Gospel verse by verse through an encyclopedic synthesis of the Fathers — Chrysostom, Jerome, Augustine — with characteristic precision on the literal sense."),
    ("Mk",    "mark",             "Mark",                      "NT", "à Lapide",
     "In Mark, à Lapide treats the shortest Gospel with characteristic concision, following the energetic Petrine narrative and drawing out its theological weight with patristic and scholastic support."),
    ("Lk",    "luke",             "Luke",                      "NT", "à Lapide",
     "À Lapide's Luke commentary is especially rich in its treatment of the Infancy narrative and the parables unique to Luke, expounding the Magnificat, the Prodigal Son, and the Good Samaritan with sustained patristic and moral depth."),
    ("Jn",    "john",             "John",                      "NT", "à Lapide",
     "In John, à Lapide rises to the heights of Johannine theology, expounding the Prologue, the bread of life discourse, and the Farewell Discourse with Augustinian and Thomistic precision, treating the Gospel as a sustained revelation of the divine Word."),
    ("1Cor",  "1corinthians",     "1 Corinthians",             "NT", "à Lapide",
     "À Lapide's 1 Corinthians commentary offers his most extended treatment of the Pauline epistles, expounding the great chapters on charity (1 Cor 13) and the resurrection (1 Cor 15) with characteristic patristic synthesis."),
    ("2Cor",  "2corinthians",     "2 Corinthians",             "NT", "à Lapide",
     "In 2 Corinthians, à Lapide expounds Paul's defence of his apostolic ministry and the theology of suffering and glory, drawing especially on Chrysostom and Theodoret."),
    ("Gal",   "galatians",        "Galatians",                 "NT", "à Lapide",
     "À Lapide's Galatians commentary treats Paul's letter on justification and law with careful attention to the anti-Pelagian tradition, expounding each verse in dialogue with Luther's errors and the Council of Trent's decrees."),
    ("1Jn",   "1john",            "1 John",                    "NT", "à Lapide",
     "In 1 John, à Lapide expounds the Apostle of love's great themes — the divine light, fraternal charity, and the discernment of spirits — drawing on Augustine's sermons and the entire mystical tradition."),
]

# Map tsv_key → metadata
BOOK_BY_KEY = {m[0]: m for m in BOOK_META}

# ─── HTML helpers ──────────────────────────────────────────────────────────────

def esc(s):
    """HTML-escape a string."""
    return html.escape(str(s), quote=False)

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


# ─── Page templates ────────────────────────────────────────────────────────────

def chapter_header(title, desc, canonical, display_name, filename, ch_num=None):
    """Header for a chapter page (lives in lapide/{book}/)."""
    if ch_num is not None:
        breadcrumb = (
            f'      <a href="../../index.html">Home</a> &rsaquo;\n'
            f'      <a href="../index.html">Cornelius à Lapide</a> &rsaquo;\n'
            f'      <a href="index.html">{esc(display_name)}</a> &rsaquo;\n'
            f'      Chapter {esc(str(ch_num))}'
        )
    else:
        breadcrumb = (
            f'      <a href="../../index.html">Home</a> &rsaquo;\n'
            f'      <a href="../index.html">Cornelius à Lapide</a> &rsaquo;\n'
            f'      {esc(display_name)}'
        )
    return f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Cornelius à Lapide | Ecclesia Dev</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="../lapide.css">
</head>
<body>

  <a href="#main-content" class="skip-nav">Skip to content</a>

  <nav aria-label="Site navigation">
    <a class="logo" href="../../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../../index.html#projects">Projects</a></li>
      <li><a href="../../articles/index.html">Articles</a></li>
      <li><a href="../index.html">À Lapide</a></li>
      <li><a href="../../index.html#about">About</a></li>
    </ul>
  </nav>

  <main id="main-content">
  <article class="article-page lapide-page">

    <div class="article-back">
{breadcrumb}
    </div>
'''


FOOTER = '''\
  </article>
  </main>

  <footer>
    <p class="motto"><em>Ad maiorem Dei gloriam</em></p>
    <p class="ichthys">&#x2625;</p>
    <p class="copy">&copy; 2026 Ecclesia Dev</p>
  </footer>

</body>
</html>
'''


def chapter_nav(filename, chapters, current_ch):
    """Render prev/next chapter navigation links."""
    idx = chapters.index(current_ch)
    prev_ch = chapters[idx - 1] if idx > 0 else None
    next_ch = chapters[idx + 1] if idx < len(chapters) - 1 else None

    parts = ['    <nav class="lapide-chapter-nav" aria-label="Chapter navigation">']
    if prev_ch is not None:
        parts.append(f'      <a class="lapide-prev" href="{prev_ch}.html">&larr; Chapter {esc(str(prev_ch))}</a>')
    else:
        parts.append('      <span class="lapide-prev lapide-nav-disabled"></span>')
    parts.append(f'      <a class="lapide-toc-link" href="index.html">All Chapters</a>')
    if next_ch is not None:
        parts.append(f'      <a class="lapide-next" href="{next_ch}.html">Chapter {esc(str(next_ch))} &rarr;</a>')
    else:
        parts.append('      <span class="lapide-next lapide-nav-disabled"></span>')
    parts.append('    </nav>')
    return '\n'.join(parts)


# ─── Load NT data (lapide.tsv: Book, Verse, Commentary) ───────────────────────
def load_nt():
    """Returns {book_key: {chapter: {verse: [commentary, ...]}}}"""
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    tsv_path = DRB_DIR / "lapide.tsv"
    with open(tsv_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i == 0 or len(row) < 3:
                continue
            book, ref, commentary = row[0].strip(), row[1].strip(), row[2].strip()
            # ref is like "1:2" or "1:2-3"
            if ':' not in ref:
                continue
            parts = ref.split(':')
            chap = parts[0].strip()
            verse = parts[1].strip()
            data[book][chap][verse].append(commentary)
    return data


# ─── Load OT data ─────────────────────────────────────────────────────────────
def load_ot_file(tsv_path):
    """Returns {chapter: {verse: [(latin_incipit, english_translation), ...]}}"""
    data = defaultdict(lambda: defaultdict(list))
    with open(tsv_path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter='\t')
        for i, row in enumerate(reader):
            if i == 0:
                continue
            if len(row) < 4:
                continue
            _book = row[0].strip()
            chap  = row[1].strip()
            verse = row[2].strip()
            if len(row) >= 5:
                latin   = row[3].strip()
                english = row[4].strip()
            else:
                latin   = ""
                english = row[3].strip()
            data[chap][verse].append((latin, english))
    return data


# ─── Render book index page ────────────────────────────────────────────────────

def render_book_index(meta, chapters_sorted, author_label):
    """Renders lapide/{book}/index.html — the chapter TOC for a book."""
    _, filename, display_name, _, author, intro = meta

    lines = []
    canonical = f"https://ecclesiadev.com/lapide/{filename}/"
    lines.append(chapter_header(
        title=display_name,
        desc=f"Commentary on {display_name} by {author_label}. Browse by chapter.",
        canonical=canonical,
        display_name=display_name,
        filename=filename,
        ch_num=None,
    ))

    lines.append(f'    <header class="article-header">')
    lines.append(f'      <h1>{esc(display_name)}</h1>')
    lines.append(f'      <p class="article-meta">{author_label} &middot; Biblical Commentary</p>')
    lines.append(f'      <p class="article-lead">{intro}</p>')
    lines.append(f'    </header>')
    lines.append(f'    <hr class="article-rule">')

    lines.append('    <nav class="lapide-chapter-grid" aria-label="Chapter list">')
    lines.append('      <h2>Chapters</h2>')
    lines.append('      <ol class="lapide-chapter-ol">')
    for ch in chapters_sorted:
        lines.append(f'        <li><a href="{ch}.html">Chapter {esc(str(ch))}</a></li>')
    lines.append('      </ol>')
    lines.append('    </nav>')

    lines.append(FOOTER)
    return '\n'.join(lines)


# ─── Render OT chapter page ────────────────────────────────────────────────────

def render_ot_chapter(meta, ch, verse_data, chapters_sorted, author_label):
    _, filename, display_name, _, author, intro = meta

    lines = []
    canonical = f"https://ecclesiadev.com/lapide/{filename}/{ch}.html"
    lines.append(chapter_header(
        title=f"{display_name} — Chapter {ch}",
        desc=f"Commentary on {display_name} chapter {ch} by {author_label}.",
        canonical=canonical,
        display_name=display_name,
        filename=filename,
        ch_num=ch,
    ))

    lines.append(chapter_nav(filename, chapters_sorted, ch))

    lines.append(f'    <header class="article-header">')
    lines.append(f'      <h1>{esc(display_name)} — Chapter {esc(str(ch))}</h1>')
    lines.append(f'      <p class="article-meta">{author_label} &middot; Biblical Commentary</p>')
    lines.append(f'    </header>')
    lines.append(f'    <hr class="article-rule">')

    verse_keys = sorted(verse_data.keys(), key=lambda v: (
        int(re.split(r'[^0-9]', v)[0]) if re.split(r'[^0-9]', v)[0].isdigit() else 0
    ))

    # verse 0 = chapter synopsis/introduction
    if '0' in verse_data:
        for (latin, english) in verse_data['0']:
            lines.append('      <div class="lapide-synopsis">')
            if latin:
                lines.append(f'        <p><em>{esc(latin)}</em></p>')
            lines.append(f'        <p>{esc(english)}</p>')
            lines.append('      </div>')

    for v in verse_keys:
        if v == '0':
            continue
        entries = verse_data[v]
        v_id = f"ch{ch}-v{v}"
        lines.append(f'      <div class="lapide-verse" id="{esc(v_id)}">')
        lines.append(f'        <h3 class="lapide-verse-ref">Verse {esc(v)}</h3>')
        for (latin, english) in entries:
            lines.append('        <div class="lapide-entry">')
            if latin:
                lines.append(f'          <p class="lapide-latin"><em>{esc(latin)}</em></p>')
            lines.append(f'          <p class="lapide-english">{esc(english)}</p>')
            lines.append('        </div>')
        lines.append('      </div>')

    lines.append(chapter_nav(filename, chapters_sorted, ch))
    lines.append(FOOTER)
    return '\n'.join(lines)


# ─── Render NT chapter page ────────────────────────────────────────────────────

def render_nt_chapter(meta, ch, verse_data, chapters_sorted):
    _, filename, display_name, _, author, intro = meta
    author_label = "Cornelius à Lapide SJ"

    lines = []
    canonical = f"https://ecclesiadev.com/lapide/{filename}/{ch}.html"
    lines.append(chapter_header(
        title=f"{display_name} — Chapter {ch}",
        desc=f"Commentary on {display_name} chapter {ch} by {author_label}.",
        canonical=canonical,
        display_name=display_name,
        filename=filename,
        ch_num=ch,
    ))

    lines.append(chapter_nav(filename, chapters_sorted, ch))

    lines.append(f'    <header class="article-header">')
    lines.append(f'      <h1>{esc(display_name)} — Chapter {esc(str(ch))}</h1>')
    lines.append(f'      <p class="article-meta">{author_label} &middot; Biblical Commentary</p>')
    lines.append(f'    </header>')
    lines.append(f'    <hr class="article-rule">')

    verse_keys = sorted(verse_data.keys(), key=lambda v: (
        int(re.split(r'[-–]', v)[0]) if re.split(r'[-–]', v)[0].isdigit() else 0
    ))

    for v in verse_keys:
        entries = verse_data[v]
        v_id = f"ch{ch}-v{v}"
        lines.append(f'      <div class="lapide-verse" id="{esc(v_id)}">')
        lines.append(f'        <h3 class="lapide-verse-ref">Verse {esc(v)}</h3>')
        for commentary in entries:
            lines.append('        <div class="lapide-entry">')
            lines.append(f'          <p class="lapide-english">{esc(commentary)}</p>')
            lines.append('        </div>')
        lines.append('      </div>')

    lines.append(chapter_nav(filename, chapters_sorted, ch))
    lines.append(FOOTER)
    return '\n'.join(lines)


# ─── Render index page ─────────────────────────────────────────────────────────
def render_index(ot_books, nt_books):
    lines = []
    lines.append('''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cornelius à Lapide — Biblical Commentary | Ecclesia Dev</title>
  <meta name="description" content="The complete biblical commentary of Cornelius à Lapide SJ (1567–1637), a monument of Jesuit exegesis and patristic synthesis. Browse by book of the Bible.">
  <link rel="canonical" href="https://ecclesiadev.com/lapide/">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="lapide.css">
</head>
<body>

  <a href="#main-content" class="skip-nav">Skip to content</a>

  <nav aria-label="Site navigation">
    <a class="logo" href="../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../index.html#projects">Projects</a></li>
      <li><a href="../articles/index.html">Articles</a></li>
      <li><a href="index.html">À Lapide</a></li>
      <li><a href="../index.html#about">About</a></li>
    </ul>
  </nav>

  <main id="main-content">
  <article class="article-page lapide-page">

    <div class="article-back">
      <a href="../index.html">Home</a> &rsaquo; Cornelius à Lapide
    </div>

    <header class="article-header">
      <h1>Cornelius à Lapide — Biblical Commentary</h1>
      <p class="article-meta">Cornelius à Lapide SJ &middot; 1567–1637</p>
      <p class="article-lead">
        Cornelius à Lapide (1567–1637) was a Flemish Jesuit who devoted his life to producing a
        commentary on almost every book of the Bible — a labour of over forty years. His work is
        one of the most encyclopedic achievements of Catholic exegesis: learned, practical, and
        saturated with the Fathers, the Scholastics, and the spiritual tradition. Drawing on
        Jerome, Augustine, Chrysostom, Thomas Aquinas, and hundreds of others, à Lapide weaves
        together the literal, allegorical, tropological, and anagogical senses with extraordinary
        care. His commentary remains a standard reference in traditional Catholic biblical study.
      </p>
      <p class="article-lead" style="margin-top:0.8rem;">
        <strong>Note on Job:</strong> The commentary on Job presented here is by
        <strong>Balthasar Corderius SJ</strong> (1592–1650), a fellow Jesuit whose learned
        catena on Job draws on the Greek Fathers and Gregory's <em>Moralia in Job</em>.
        It is included here as a companion to the Lapide series.
      </p>
    </header>
    <hr class="article-rule">

    <div class="lapide-index-grid">

      <section>
        <h2>Old Testament</h2>
        <ul class="lapide-book-list">
''')

    for key, filename, display_name, _, author, _ in ot_books:
        badge = ' <span class="lapide-badge">Corderius</span>' if author == "Corderius" else ''
        lines.append(f'          <li><a href="{filename}/index.html">{esc(display_name)}</a>{badge}</li>')

    lines.append('''\
        </ul>
      </section>

      <section>
        <h2>New Testament</h2>
        <ul class="lapide-book-list">
''')

    for key, filename, display_name, _, author, _ in nt_books:
        lines.append(f'          <li><a href="{filename}/index.html">{esc(display_name)}</a></li>')

    lines.append('''\
        </ul>
      </section>

    </div><!-- /.lapide-index-grid -->

  </article>
  </main>

  <footer>
    <p class="motto"><em>Ad maiorem Dei gloriam</em></p>
    <p class="ichthys">&#x2625;</p>
    <p class="copy">&copy; 2026 Ecclesia Dev</p>
  </footer>

</body>
</html>
''')

    return '\n'.join(lines)


# ─── Supplemental CSS ──────────────────────────────────────────────────────────
LAPIDE_CSS = '''\
/* === Lapide Commentary Browser === */

.lapide-page .article-header h1 {
  font-size: 2rem;
}

.lapide-toc {
  background: var(--bg-code);
  padding: 1.2rem 1.6rem;
  margin-bottom: 2.5rem;
  border-left: 3px solid var(--liturgical-dim);
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0;
  align-items: baseline;
}

.lapide-toc .toc-title {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-right: 1rem;
  flex: 0 0 100%;
  margin-bottom: 0.5rem;
}

.lapide-toc ol {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem 0.8rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

.lapide-toc li {
  margin: 0;
  font-size: 0.92rem;
}

.lapide-toc a {
  color: var(--liturgical-color);
}

.lapide-toc a:hover {
  color: var(--text);
  text-decoration: none;
}

/* Chapter navigation */
.lapide-chapter-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 0;
  margin: 1.5rem 0;
  border-top: 1px solid var(--border);
  border-bottom: 1px solid var(--border);
  font-size: 0.95rem;
}

.lapide-chapter-nav a {
  color: var(--liturgical-color);
  text-decoration: none;
}

.lapide-chapter-nav a:hover {
  color: var(--text);
}

.lapide-toc-link {
  font-size: 0.85rem;
  color: var(--text-muted) !important;
}

.lapide-nav-disabled {
  display: inline-block;
  width: 6rem;
}

/* Chapter list on book index */
.lapide-chapter-grid h2 {
  font-size: 1.3rem;
  margin-bottom: 1rem;
}

.lapide-chapter-ol {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 1rem;
  padding: 0;
  margin: 0;
  list-style: none;
}

.lapide-chapter-ol li {
  font-size: 0.97rem;
}

.lapide-chapter-ol a {
  color: var(--liturgical-color);
}

.lapide-chapter-ol a:hover {
  color: var(--text);
  text-decoration: none;
}

/* Sections */
.lapide-page section {
  margin-bottom: 3rem;
}

.lapide-page section h2 {
  font-size: 1.5rem;
  color: var(--liturgical-color);
  margin-bottom: 1.2rem;
  padding-bottom: 0.3rem;
  border-bottom: 1px solid var(--border);
  text-transform: none;
  letter-spacing: 0;
}

/* Chapter synopsis */
.lapide-synopsis {
  background: var(--bg-code);
  border-left: 3px solid var(--liturgical-dim);
  padding: 0.9rem 1.2rem;
  margin-bottom: 1.5rem;
  font-style: italic;
  color: var(--text-muted);
}

.lapide-synopsis p {
  margin-bottom: 0.5rem;
}

.lapide-synopsis p:last-child {
  margin-bottom: 0;
}

/* Verse */
.lapide-verse {
  margin-bottom: 1.8rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}

.lapide-verse:last-child {
  border-bottom: none;
}

.lapide-verse-ref {
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 600;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
  text-transform: none;
}

.lapide-entry {
  margin-bottom: 0.8rem;
}

.lapide-latin {
  color: var(--text-muted);
  margin-bottom: 0.3rem;
  font-size: 0.97rem;
}

.lapide-english {
  margin-bottom: 0;
  line-height: 1.8;
}

/* Index grid */
.lapide-index-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem 4rem;
  margin-top: 1rem;
}

@media (max-width: 600px) {
  .lapide-index-grid {
    grid-template-columns: 1fr;
  }
}

.lapide-book-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.lapide-book-list li {
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 1rem;
}

.lapide-book-list li:first-child {
  border-top: 1px solid var(--border);
}

.lapide-book-list a {
  color: var(--text);
}

.lapide-book-list a:hover {
  color: var(--liturgical-color);
  text-decoration: none;
}

.lapide-badge {
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-muted);
  border: 1px solid var(--border);
  padding: 0.1em 0.4em;
  margin-left: 0.5em;
  vertical-align: middle;
}
'''


# ─── Main ──────────────────────────────────────────────────────────────────────
def main():
    ot_meta = [m for m in BOOK_META if m[3] == "OT"]
    nt_meta = [m for m in BOOK_META if m[3] == "NT"]

    nt_data = load_nt()

    generated_files = []
    generated_dirs = []

    # Write supplemental CSS
    css_path = OUTPUT_DIR / "lapide.css"
    css_path.write_text(LAPIDE_CSS, encoding="utf-8")
    print(f"  CSS: {css_path}")

    # Remove old monolithic book HTML files (e.g. lapide/john.html)
    old_html = list(OUTPUT_DIR.glob("*.html"))
    old_book_html = [p for p in old_html if p.name != "index.html"]
    for p in old_book_html:
        p.unlink()
        print(f"  DEL: {p.name}")

    # Generate OT pages
    for meta in ot_meta:
        key, filename, display_name, _, author, _ = meta
        author_label = "Cornelius à Lapide SJ" if author == "à Lapide" else "Balthasar Corderius SJ"

        if key == "Jb":
            tsv_path = DRB_DIR / "corderius-Jb.tsv"
        else:
            tsv_path = DRB_DIR / f"lapide-{key}.tsv"

        if not tsv_path.exists():
            print(f"  SKIP (no file): {tsv_path}")
            continue

        chap_data = load_ot_file(tsv_path)
        if not chap_data:
            print(f"  SKIP (empty): {key}")
            continue

        chapters_sorted = sorted(chap_data.keys(), key=lambda c: int(c) if c.isdigit() else 0)

        # Create book subdirectory
        book_dir = OUTPUT_DIR / filename
        book_dir.mkdir(exist_ok=True)

        # Write book index (chapter TOC)
        index_html = render_book_index(meta, chapters_sorted, author_label)
        index_path = book_dir / "index.html"
        index_path.write_text(index_html, encoding="utf-8")

        # Write per-chapter pages
        for ch in chapters_sorted:
            ch_html = render_ot_chapter(meta, ch, chap_data[ch], chapters_sorted, author_label)
            ch_path = book_dir / f"{ch}.html"
            ch_path.write_text(ch_html, encoding="utf-8")

        print(f"  OT: {filename}/ ({len(chapters_sorted)} chapters)")
        generated_dirs.append(filename)

    # Generate NT pages
    for meta in nt_meta:
        key, filename, display_name, _, author, _ = meta

        if key not in nt_data:
            print(f"  SKIP (no NT data): {key}")
            continue

        chap_data = nt_data[key]
        chapters_sorted = sorted(chap_data.keys(), key=lambda c: int(c) if c.isdigit() else 0)

        # Create book subdirectory
        book_dir = OUTPUT_DIR / filename
        book_dir.mkdir(exist_ok=True)

        # Write book index (chapter TOC)
        index_html = render_book_index(meta, chapters_sorted, "Cornelius à Lapide SJ")
        index_path = book_dir / "index.html"
        index_path.write_text(index_html, encoding="utf-8")

        # Write per-chapter pages
        for ch in chapters_sorted:
            ch_html = render_nt_chapter(meta, ch, chap_data[ch], chapters_sorted)
            ch_path = book_dir / f"{ch}.html"
            ch_path.write_text(ch_html, encoding="utf-8")

        print(f"  NT: {filename}/ ({len(chapters_sorted)} chapters)")
        generated_dirs.append(filename)

    # Generate master index
    index_html = render_index(ot_meta, nt_meta)
    index_path = OUTPUT_DIR / "index.html"
    index_path.write_text(index_html, encoding="utf-8")
    print(f"  INDEX: {index_path}")

    print(f"\nDone. Generated {len(generated_dirs)} book directories.")
    return generated_dirs


if __name__ == "__main__":
    main()
