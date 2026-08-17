#!/usr/bin/env python3
"""Builds the note's four language pages from an existing note as the template.

The site keeps its CSS inline per page, so a new note is made by taking the last
one, swapping the metadata and the body, and rewriting the language switcher.
Copying the file rather than hand-writing the shell keeps every page's styling
identical, which is the only reason the site looks consistent at all.
"""
import re, os, sys, json

SITE = os.path.expanduser('~/repo/recilic-site')
SLUG = 'mesh-went-quiet'
TEMPLATE_SLUG = 'lan-line-rate'

META = json.load(open('/tmp/note/meta.json'))
BODIES = {lang: open(f'/tmp/note/{lang}-body.html').read().rstrip() for lang in META}

# ("directory prefix", "html lang attribute", "label in the switcher")
LOCALES = {
    'en': ('', 'en'),
    'zh': ('zh/', 'zh-Hant'),
    'ja': ('ja/', 'ja'),
    'ko': ('ko/', 'ko'),
}


def switcher(lang):
    """The language row, with the current language marked active."""
    order = [('zh', '中文'), ('ja', '日本語'), ('ko', '한국어'), ('en', 'EN')]
    parts = []
    for code, label in order:
        prefix = LOCALES[code][0]
        active = ' class="active"' if code == lang else ''
        parts.append(f'<a{active} href="/{prefix}notes/{SLUG}/">{label}</a>')
    return '<span class="lang">' + '|'.join(parts) + '</span>'


for lang, (prefix, html_lang) in LOCALES.items():
    template_path = f'{SITE}/{prefix}notes/{TEMPLATE_SLUG}/index.html'
    page = open(template_path).read()
    meta = META[lang]

    # Head: title, description and the social card.
    page = re.sub(r'<title>.*?</title>', f'<title>{meta["title"]} · Recilic</title>', page, flags=re.S)
    page = re.sub(r'(<meta name="description" content=").*?(">)', lambda m: m.group(1) + meta['description'] + m.group(2), page, flags=re.S)
    page = re.sub(r'(<meta property="og:title" content=").*?(">)', lambda m: m.group(1) + meta['title'] + m.group(2), page, flags=re.S)
    page = re.sub(r'(<meta property="og:description" content=").*?(">)', lambda m: m.group(1) + meta['description'] + m.group(2), page, flags=re.S)
    page = page.replace(f'https://recilic.app/{prefix}notes/{TEMPLATE_SLUG}/',
                        f'https://recilic.app/{prefix}notes/{SLUG}/')
    page = page.replace(f'og-card-{TEMPLATE_SLUG}.png', f'og-card-{SLUG}.png')
    page = page.replace(f'<html lang="{html_lang}">', f'<html lang="{html_lang}">')

    # The language switcher points at this note in every language.
    page = re.sub(r'<span class="lang">.*?</span>', switcher(lang), page, flags=re.S)

    # Body: everything between the breadcrumb and the closing </main>.
    start = page.index('    <p class="crumb">')
    end = page.index('  </main>')
    page = page[:start] + BODIES[lang] + '\n' + page[end:]

    out_dir = f'{SITE}/{prefix}notes/{SLUG}'
    os.makedirs(out_dir, exist_ok=True)
    with open(f'{out_dir}/index.html', 'w') as f:
        f.write(page)

    # Cheap structural checks: a note that lost its stylesheet or its switcher
    # looks broken in a way that is easy to ship and embarrassing to find later.
    problems = []
    if '<style>' not in page:
        problems.append('lost the inline stylesheet')
    if page.count('class="lang"') != 1:
        problems.append('language switcher missing or duplicated')
    if TEMPLATE_SLUG in page:
        problems.append(f'still references the template note ({TEMPLATE_SLUG})')
    if meta['title'] not in page:
        problems.append('title did not land')
    print(f'{prefix or "en/":8} {len(page):6} bytes  ' + ('; '.join(problems) if problems else 'ok'))
    if problems:
        sys.exit(1)
