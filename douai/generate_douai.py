#!/usr/bin/env python3
"""
Generate Douai-Rheims 1609 Annotations browser HTML.
Modeled on the Lapide commentary browser.
"""

import os
import csv
import html
from collections import defaultdict, OrderedDict
from pathlib import Path

# ── Book abbreviation → (dirname, display name) ───────────────────────────────
BOOK_MAP = {
    'Gn':    ('genesis',          'Genesis'),
    'Ex':    ('exodus',           'Exodus'),
    'Lv':    ('leviticus',        'Leviticus'),
    'Nm':    ('numbers',          'Numbers'),
    'Dt':    ('deuteronomy',      'Deuteronomy'),
    'Jos':   ('joshua',           'Joshua'),
    'Jgs':   ('judges',           'Judges'),
    'Ru':    ('ruth',             'Ruth'),
    '1Sam':  ('1samuel',          '1 Samuel'),
    '2Sam':  ('2samuel',          '2 Samuel'),
    '1Kings':('1kings',           '1 Kings'),
    '2Kings':('2kings',           '2 Kings'),
    '1Chr':  ('1chronicles',      '1 Chronicles'),
    '2Chr':  ('2chronicles',      '2 Chronicles'),
    'Ezr':   ('ezra',             'Ezra'),
    'Neh':   ('nehemiah',         'Nehemiah'),
    'Tb':    ('tobit',            'Tobit'),
    'Jdt':   ('judith',           'Judith'),
    'Est':   ('esther',           'Esther'),
    '1Mc':   ('1maccabees',       '1 Maccabees'),
    '2Mc':   ('2maccabees',       '2 Maccabees'),
    'Jb':    ('job',              'Job'),
    'Ps':    ('psalms',           'Psalms'),
    'Prv':   ('proverbs',         'Proverbs'),
    'Eccl':  ('ecclesiastes',     'Ecclesiastes'),
    'Sg':    ('canticleofcanticles', 'Canticle of Canticles'),
    'Wis':   ('wisdom',           'Wisdom'),
    'Sir':   ('sirach',           'Sirach'),
    'Is':    ('isaiah',           'Isaiah'),
    'Jer':   ('jeremiah',         'Jeremiah'),
    'Lam':   ('lamentations',     'Lamentations'),
    'Bar':   ('baruch',           'Baruch'),
    'Ez':    ('ezekiel',          'Ezekiel'),
    'Dn':    ('daniel',           'Daniel'),
    'Hos':   ('hosea',            'Hosea'),
    'Jl':    ('joel',             'Joel'),
    'Am':    ('amos',             'Amos'),
    'Mt':    ('matthew',          'Matthew'),
    'Mk':    ('mark',             'Mark'),
    'Lk':    ('luke',             'Luke'),
    'Jn':    ('john',             'John'),
    'Rom':   ('romans',           'Romans'),
    '1Cor':  ('1corinthians',     '1 Corinthians'),
    '2Cor':  ('2corinthians',     '2 Corinthians'),
    'Gal':   ('galatians',        'Galatians'),
    'Eph':   ('ephesians',        'Ephesians'),
    'Phil':  ('philippians',      'Philippians'),
    'Col':   ('colossians',       'Colossians'),
    '1Thes': ('1thessalonians',   '1 Thessalonians'),
    '2Thes': ('2thessalonians',   '2 Thessalonians'),
    '1Tim':  ('1timothy',         '1 Timothy'),
    '2Tim':  ('2timothy',         '2 Timothy'),
    'Tit':   ('titus',            'Titus'),
    'Phlm':  ('philemon',         'Philemon'),
    'Heb':   ('hebrews',          'Hebrews'),
    'Jude':  ('jude',             'Jude'),
    'Apc':   ('revelation',       'Revelation'),
}

OT_ABBREVS = ['Gn','Ex','Lv','Nm','Dt','Jos','Jgs','Ru','1Sam','2Sam','1Kings','2Kings',
              '1Chr','2Chr','Ezr','Neh','Tb','Jdt','Est','1Mc','2Mc','Jb','Ps','Prv',
              'Eccl','Sg','Wis','Sir','Is','Jer','Lam','Bar','Ez','Dn','Hos','Jl','Am']
NT_ABBREVS = ['Mt','Mk','Lk','Jn','Rom','1Cor','2Cor','Gal','Eph','Phil','Col',
              '1Thes','2Thes','1Tim','2Tim','Tit','Phlm','Heb','Jude','Apc']

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
TSV_PATH   = SCRIPT_DIR.parent.parent / "drb-ios" / "DouayRheims" / "douai-1609-fixed-v9.tsv"
OUT_DIR    = SCRIPT_DIR   # output relative to this script's directory


def esc(s):
    return html.escape(s, quote=False)


def nav_html(active='douai'):
    return '''\
  <nav aria-label="Site navigation">
    <a class="logo" href="../../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../../index.html#projects">Projects</a></li>
      <li><a href="../../articles/index.html">Articles</a></li>
      <li><a href="../index.html">Douai-Rheims 1609</a></li>
      <li><a href="../../index.html#about">About</a></li>
    </ul>
  </nav>'''


def footer_html():
    return '''\
  <footer>
    <p class="motto"><em>Ad maiorem Dei gloriam</em></p>
    <p class="ichthys">&#x2625;</p>
    <p class="copy">&copy; 2026 Ecclesia Dev</p>
  </footer>'''


def source_short(abbrev):
    """Short label for meta description: '1609 Douay Old Testament' or '1582 Rheims New Testament'."""
    if abbrev in NT_ABBREVS:
        return '1582 Rheims New Testament'
    return '1609 Douay Old Testament'


def source_long(abbrev):
    """Full sentence for inline note on chapter pages."""
    if abbrev in NT_ABBREVS:
        return (
            'These annotations are from the original 1582 Rheims New Testament, '
            'produced by English scholars in exile at the English College of Rheims. '
            'The archaic spelling is preserved.'
        )
    return (
        'These annotations are from the original 1609 Douay Old Testament, '
        'the first complete English Catholic Bible translation, '
        'produced by English scholars in exile at the English College of Douai. '
        'The archaic spelling is preserved.'
    )


def note_html(abbrev=''):
    return (
        '<p class="lapide-synopsis" style="font-style:normal;">'
        + source_long(abbrev) +
        '</p>'
    )


# ── Parse TSV ─────────────────────────────────────────────────────────────────
def parse_tsv(path):
    """
    Returns: dict[abbrev → dict[chapter_int → dict[verse_int → [annotations]]]]
    Preserves canonical chapter/verse order.
    """
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 3:
                continue
            abbrev, cv, annotation = row[0].strip(), row[1].strip(), row[2].strip()
            # Skip header rows
            if abbrev == 'BookAbbrev' or abbrev == '':
                continue
            if abbrev not in BOOK_MAP:
                continue  # unknown book
            # Parse chapter:verse
            if ':' not in cv:
                continue
            ch_str, v_str = cv.split(':', 1)
            try:
                ch = int(ch_str)
                v  = int(v_str)
            except ValueError:
                continue
            data[abbrev][ch][v].append(annotation)

    return data


# ── Build index.html ──────────────────────────────────────────────────────────
def build_index(data, out_dir):
    """Main douai/index.html listing all books."""
    ot_rows = []
    nt_rows = []

    for abbrev in OT_ABBREVS:
        if abbrev not in data:
            continue
        dirname, display = BOOK_MAP[abbrev]
        ch_count = len(data[abbrev])
        ot_rows.append(
            f'          <li><a href="{dirname}/index.html">{esc(display)}</a>'
            f' <span class="lapide-badge">{ch_count} ch.</span></li>'
        )

    for abbrev in NT_ABBREVS:
        if abbrev not in data:
            continue
        dirname, display = BOOK_MAP[abbrev]
        ch_count = len(data[abbrev])
        nt_rows.append(
            f'          <li><a href="{dirname}/index.html">{esc(display)}</a>'
            f' <span class="lapide-badge">{ch_count} ch.</span></li>'
        )

    ot_section = ''
    if ot_rows:
        ot_section = (
            '      <section>\n'
            '        <h2>Old Testament</h2>\n'
            '        <ul class="lapide-book-list">\n'
            + '\n'.join(ot_rows) + '\n'
            '        </ul>\n'
            '      </section>'
        )

    nt_section = ''
    if nt_rows:
        nt_section = (
            '      <section>\n'
            '        <h2>New Testament</h2>\n'
            '        <ul class="lapide-book-list">\n'
            + '\n'.join(nt_rows) + '\n'
            '        </ul>\n'
            '      </section>'
        )

    content = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Douai-Rheims 1609 Annotations | Ecclesia Dev</title>
  <meta name="description" content="Annotations from the Douay-Rheims Bible: the 1609 Douay Old Testament and the 1582 Rheims New Testament. Browse by book and chapter.">
  <link rel="canonical" href="https://ecclesiadev.com/douai/">
  <link rel="icon" type="image/svg+xml" href="../favicon.svg">
  <link rel="stylesheet" href="../style.css">
  <link rel="stylesheet" href="douai.css">
</head>
<body>

  <a href="#main-content" class="skip-nav">Skip to content</a>

  <nav aria-label="Site navigation">
    <a class="logo" href="../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../index.html#projects">Projects</a></li>
      <li><a href="../articles/index.html">Articles</a></li>
      <li><a href="index.html">Douai-Rheims 1609</a></li>
      <li><a href="../index.html#about">About</a></li>
    </ul>
  </nav>

  <main id="main-content">
  <article class="article-page lapide-page">

    <div class="article-back">
      <a href="../index.html">Home</a> &rsaquo; Douai-Rheims 1609 Annotations
    </div>

    <header class="article-header">
      <h1>Douay-Rheims — Annotations</h1>
      <p class="article-meta">Rheims New Testament (1582) &middot; Douay Old Testament (1609)</p>
      <p class="article-lead">
        The Douay-Rheims is the first complete English Catholic Bible translation, produced by
        English scholars in exile. The New Testament was published at Rheims in 1582; the Old
        Testament at Douai in 1609. Each book was accompanied by extensive marginal and chapter
        annotations explaining the text, defending Catholic doctrine, and offering patristic
        commentary. These annotations are preserved here verbatim, with all archaic spelling intact.
      </p>
    </header>
    <hr class="article-rule">

    <div class="lapide-index-grid">

{ot_section}

{nt_section}

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
'''
    out_path = out_dir / 'index.html'
    out_path.write_text(content, encoding='utf-8')
    print(f'  wrote {out_path}')


# ── Build book index ──────────────────────────────────────────────────────────
def build_book_index(abbrev, chapters, out_dir):
    dirname, display = BOOK_MAP[abbrev]
    book_dir = out_dir / dirname
    book_dir.mkdir(parents=True, exist_ok=True)

    sorted_chapters = sorted(chapters.keys())
    ch_items = '\n'.join(
        f'        <li><a href="{ch}.html">Chapter {ch}</a></li>'
        for ch in sorted_chapters
    )

    content = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(display)} | Douai-Rheims 1609 | Ecclesia Dev</title>
  <meta name="description" content="Annotations on {esc(display)} from the {source_short(abbrev)}. Browse by chapter.">
  <link rel="canonical" href="https://ecclesiadev.com/douai/{dirname}/">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="../douai.css">
</head>
<body>

  <a href="#main-content" class="skip-nav">Skip to content</a>

  <nav aria-label="Site navigation">
    <a class="logo" href="../../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../../index.html#projects">Projects</a></li>
      <li><a href="../../articles/index.html">Articles</a></li>
      <li><a href="../index.html">Douai-Rheims 1609</a></li>
      <li><a href="../../index.html#about">About</a></li>
    </ul>
  </nav>

  <main id="main-content">
  <article class="article-page lapide-page">

    <div class="article-back">
      <a href="../../index.html">Home</a> &rsaquo;
      <a href="../index.html">Douai-Rheims 1609</a> &rsaquo;
      {esc(display)}
    </div>

    <header class="article-header">
      <h1>{esc(display)}</h1>
      <p class="article-meta">Douai-Rheims 1609 &middot; Annotations</p>
    </header>
    <hr class="article-rule">
    <nav class="lapide-chapter-grid" aria-label="Chapter list">
      <h2>Chapters</h2>
      <ol class="lapide-chapter-ol">
{ch_items}
      </ol>
    </nav>
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
    out_path = book_dir / 'index.html'
    out_path.write_text(content, encoding='utf-8')


# ── Build chapter page ────────────────────────────────────────────────────────
def build_chapter(abbrev, ch, verses, all_chapters, out_dir):
    dirname, display = BOOK_MAP[abbrev]
    book_dir = out_dir / dirname

    sorted_chapters = sorted(all_chapters)
    ch_index = sorted_chapters.index(ch)
    prev_ch = sorted_chapters[ch_index - 1] if ch_index > 0 else None
    next_ch = sorted_chapters[ch_index + 1] if ch_index < len(sorted_chapters) - 1 else None

    # Prev / next nav
    if prev_ch:
        prev_link = f'<a class="lapide-prev" href="{prev_ch}.html">&larr; Chapter {prev_ch}</a>'
    else:
        prev_link = '<span class="lapide-prev lapide-nav-disabled"></span>'

    if next_ch:
        next_link = f'<a class="lapide-next" href="{next_ch}.html">Chapter {next_ch} &rarr;</a>'
    else:
        next_link = '<span class="lapide-next lapide-nav-disabled"></span>'

    # TOC (verse refs)
    sorted_verses = sorted(verses.keys())
    toc_items = ' '.join(
        f'<li><a href="#ch{ch}-v{v}">{v}</a></li>'
        for v in sorted_verses
    )

    # Verse blocks
    verse_blocks = []
    for v in sorted_verses:
        annotations = verses[v]
        entries = '\n'.join(
            f'          <div class="lapide-entry">\n'
            f'            <p class="lapide-english">{esc(ann)}</p>\n'
            f'          </div>'
            for ann in annotations
        )
        verse_blocks.append(
            f'      <div class="lapide-verse" id="ch{ch}-v{v}">\n'
            f'        <h3 class="lapide-verse-ref">Verse {v}</h3>\n'
            f'{entries}\n'
            f'      </div>'
        )

    verses_html = '\n'.join(verse_blocks)

    content = f'''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(display)} — Chapter {ch} | Douai-Rheims 1609 | Ecclesia Dev</title>
  <meta name="description" content="Annotations on {esc(display)} chapter {ch} from the {source_short(abbrev)}.">
  <link rel="canonical" href="https://ecclesiadev.com/douai/{dirname}/{ch}.html">
  <link rel="icon" type="image/svg+xml" href="../../favicon.svg">
  <link rel="stylesheet" href="../../style.css">
  <link rel="stylesheet" href="../douai.css">
</head>
<body>

  <a href="#main-content" class="skip-nav">Skip to content</a>

  <nav aria-label="Site navigation">
    <a class="logo" href="../../index.html">✝ Ecclesia Dev</a>
    <ul>
      <li><a href="../../index.html#projects">Projects</a></li>
      <li><a href="../../articles/index.html">Articles</a></li>
      <li><a href="../index.html">Douai-Rheims 1609</a></li>
      <li><a href="../../index.html#about">About</a></li>
    </ul>
  </nav>

  <main id="main-content">
  <article class="article-page lapide-page">

    <div class="article-back">
      <a href="../../index.html">Home</a> &rsaquo;
      <a href="../index.html">Douai-Rheims 1609</a> &rsaquo;
      <a href="index.html">{esc(display)}</a> &rsaquo;
      Chapter {ch}
    </div>

    <nav class="lapide-chapter-nav" aria-label="Chapter navigation">
      {prev_link}
      <a class="lapide-toc-link" href="index.html">All Chapters</a>
      {next_link}
    </nav>

    <header class="article-header">
      <h1>{esc(display)} &mdash; Chapter {ch}</h1>
      <p class="article-meta">Douai-Rheims 1609 &middot; Annotations</p>
    </header>
    <hr class="article-rule">

    <div class="lapide-synopsis">
      <p>{source_long(abbrev)}</p>
    </div>

    <nav class="lapide-toc" aria-label="Verse list">
      <span class="toc-title">Verses annotated</span>
      <ol>
        {toc_items}
      </ol>
    </nav>

    <section>
{verses_html}
    </section>

    <nav class="lapide-chapter-nav" aria-label="Chapter navigation">
      {prev_link}
      <a class="lapide-toc-link" href="index.html">All Chapters</a>
      {next_link}
    </nav>

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
    out_path = book_dir / f'{ch}.html'
    out_path.write_text(content, encoding='utf-8')


# ── Build CSS ─────────────────────────────────────────────────────────────────
def build_css(out_dir):
    lapide_css_path = Path(__file__).parent.parent / 'lapide' / 'lapide.css'
    css = lapide_css_path.read_text(encoding='utf-8')
    # Update comment header
    css = css.replace('/* === Lapide Commentary Browser === */',
                      '/* === Douai-Rheims 1609 Annotations Browser === */')
    out_path = out_dir / 'douai.css'
    out_path.write_text(css, encoding='utf-8')
    print(f'  wrote {out_path}')


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    print('Parsing TSV …')
    data = parse_tsv(TSV_PATH)

    books_found = len(data)
    total_pages = sum(len(chs) for chs in data.values())
    print(f'  found {books_found} books, {total_pages} chapters total')

    print('Building CSS …')
    build_css(OUT_DIR)

    print('Building index.html …')
    build_index(data, OUT_DIR)

    print('Building book and chapter pages …')
    page_count = 0
    for abbrev in OT_ABBREVS + NT_ABBREVS:
        if abbrev not in data:
            continue
        dirname, display = BOOK_MAP[abbrev]
        chapters = data[abbrev]
        build_book_index(abbrev, chapters, OUT_DIR)
        page_count += 1
        all_chs = list(chapters.keys())
        for ch, verses in chapters.items():
            build_chapter(abbrev, ch, verses, all_chs, OUT_DIR)
            page_count += 1

    print(f'\nDone — {books_found} books, {page_count} pages written to {OUT_DIR}')
    print(f'  (index + {books_found} book indexes + {total_pages} chapter pages)')


if __name__ == '__main__':
    main()
