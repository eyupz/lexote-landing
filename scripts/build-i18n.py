#!/usr/bin/env python3
"""Build static English pages from the reviewed Turkish/English catalogue.

No runtime translation service. Unknown Turkish copy stops the build so source
changes cannot silently leave the English version incomplete.
"""
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
BASE = 'https://lexote.com.tr'
SOURCE = json.loads((ROOT / 'i18n/source-tr.json').read_text())
ENGLISH = json.loads((ROOT / 'i18n/en.json').read_text())
SHARED = {
    'Hâlâ gün mü sayıyorsunuz? — Lexote': 'Still counting days? — Lexote',
    'Dosyalar sizi bekliyor — Lexote': 'Your cases are waiting — Lexote',
    'Son gün sürpriz olmasın — Lexote': 'Stay ahead of your deadlines — Lexote',
    'Davalarınız bekliyor — Lexote': 'Your cases are waiting — Lexote',
    'Notlarınız sizi bekliyor — Lexote': 'Your notes are waiting — Lexote',
    'Süreniz dolmadan dönün — Lexote': 'Return before your deadline — Lexote',
    'Hukuki süreciniz devam ediyor — Lexote': 'Your legal work continues — Lexote',
    'Menüyü kapat': 'Close menu',
    'Menüyü aç': 'Open menu',
}

def normal(s):
    return ' '.join(s.split())

class Translate(HTMLParser):
    def __init__(self, mapping):
        super().__init__(convert_charrefs=True)
        self.mapping = mapping
        self.out = []
        self.stack = []
        self.missing = set()

    def translated(self, value):
        key = normal(value)
        if not key:
            return value
        if key in self.mapping:
            leading = re.match(r'^\s*', value).group()
            trailing = re.search(r'\s*$', value).group()
            translated = self.mapping[key]
            if translated.startswith(('.', ',', ';', ':', '!', '?')):
                leading = ''
            return leading + translated + trailing
        if key in ('TR', 'EN', 'Türkçe', 'English', 'Language / Dil'):
            return value
        self.missing.add(key)
        return value

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        skipped = any(t in ('script', 'style', 'svg') for t in self.stack)
        if not skipped and tag not in ('script', 'style', 'svg'):
            meta_copy = tag == 'meta' and any(v in ('description', 'og:title', 'og:description', 'og:image:alt', 'twitter:title', 'twitter:description') for _, v in attrs)
            for key, value in attrs:
                if value and (key in ('aria-label', 'alt', 'title') or (meta_copy and key == 'content')):
                    translated = self.translated(value)
                    raw = re.sub(r'(\b' + re.escape(key) + r'\s*=\s*)(["\x27])(.*?)\2', lambda m: m.group(1) + '"' + escape(translated, quote=True) + '"', raw, count=1, flags=re.S)
        self.out.append(raw)
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_endtag(self, tag):
        self.out.append('</' + tag + '>')
        if tag in self.stack:
            self.stack = self.stack[:len(self.stack) - 1 - self.stack[::-1].index(tag)]

    def handle_data(self, data):
        if any(t in ('script', 'style', 'svg') for t in self.stack):
            if 'script' in self.stack:
                for tr, en in SHARED.items():
                    data = data.replace(tr, en)
            self.out.append(data)
        else:
            self.out.append(escape(self.translated(data), quote=False))

    def handle_comment(self, data):
        # Source comments stay in Turkish; they are not user-facing copy.
        self.out.append('<!--' + data + '-->')

    def handle_decl(self, decl):
        self.out.append('<!' + decl + '>')

class FAQs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_details = False
        self.in_summary = False
        self.question = []
        self.answer = []
        self.items = []
    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            self.in_details = True
            self.question, self.answer = [], []
        elif tag == 'summary':
            self.in_summary = True
    def handle_endtag(self, tag):
        if tag == 'summary':
            self.in_summary = False
        if tag == 'details' and self.in_details:
            self.items.append({'@type': 'Question', 'name': normal(''.join(self.question)), 'acceptedAnswer': {'@type': 'Answer', 'text': normal(''.join(self.answer))}})
            self.in_details = False
    def handle_data(self, data):
        if self.in_details:
            (self.question if self.in_summary else self.answer).append(data)

def localize_schema(document):
    def replace(match):
        schema = json.loads(match.group(1))
        faqs = FAQs()
        faqs.feed(document)
        for node in schema.get('@graph', []):
            kind = node.get('@type')
            if kind == 'WebSite':
                node['inLanguage'] = ['tr', 'en']
            if kind == 'MobileApplication':
                node['description'] = 'Deadline and case note tracking for lawyers practising in Türkiye. Enter the date of service, calculate the deadline and get reminders before it arrives.'
                node['audience']['audienceType'] = 'Lawyers'
                node['featureList'] = [
                    'Calculate a due date from the date of service and a time limit (HMK, Article 92)',
                    'Information on holidays, electronic service, working days and the judicial recess (HMK, Articles 93 and 104; Turkish Notification Law, Article 7/a)',
                    'Colour-coded urgency indicators and deadline filters',
                    'Critical reminders 24, 12, 6 and 1 hour before a deadline, and a notification when it expires',
                    'An in-app calendar showing notes due each day',
                    'Case notes and voice notes',
                    'Guest use without creating an account',
                ]
            if kind == 'FAQPage':
                node['@id'] = BASE + '/en/#sss'
                node['inLanguage'] = 'en'
                node['mainEntity'] = faqs.items
        return '<script type="application/ld+json">\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n  </script>'
    return re.sub(r'<script type="application/ld\+json">(.*?)</script>', replace, document, flags=re.S)

def main():
    target = ROOT / 'en'
    target.mkdir(exist_ok=True)
    for filename, source in SOURCE.items():
        translated = ENGLISH[filename]
        if len(source) != len(translated):
            raise ValueError(f'{filename}: translation count differs from source')
        mapping = dict(zip(source, translated))
        mapping.update(SHARED)
        parser = Translate(mapping)
        parser.feed((ROOT / filename).read_text())
        if parser.missing:
            raise ValueError(f'{filename}: unreviewed copy: {sorted(parser.missing)}')
        output = ''.join(parser.out).replace('<html lang="tr">', '<html lang="en">')
        # Assets are shared from the site root; page links remain in /en/.
        for prefix in ('fonts/', 'img/', 'media/', 'styles.css', 'language.js'):
            output = output.replace('"' + prefix, '"/' + prefix).replace("'" + prefix, "'/" + prefix)
        output = output.replace('https://apps.apple.com/tr/', 'https://apps.apple.com/')
        output = output.replace('content="tr_TR"', 'content="en_GB"')
        output = output.replace('property="og:locale:alternate" content="en_GB"', 'property="og:locale:alternate" content="tr_TR"')
        page_path = '' if filename == 'index.html' else filename
        output = output.replace(f'rel="canonical" href="{BASE}/{page_path}"', f'rel="canonical" href="{BASE}/en/{page_path}"')
        output = output.replace(f'property="og:url" content="{BASE}/"', f'property="og:url" content="{BASE}/en/"')
        # Language navigation uses static links, including when JavaScript is off.
        output = output.replace('hreflang="tr" lang="tr" aria-current="page"', 'hreflang="tr" lang="tr"')
        output = output.replace('hreflang="en" lang="en"', 'hreflang="en" lang="en" aria-current="page"')
        if filename == '404.html':
            output = output.replace('href="/"', 'href="/en/"')
        if filename == 'index.html':
            output = localize_schema(output)
        output = output.replace('href="/site.webmanifest"', 'href="/en/site.webmanifest"')
        (target / filename).write_text(output)
        print(f'en/{filename}: {len(source)} reviewed strings')
    # Verification copy is already bilingual. Its controls switch in place so
    # the one-time verification code is never copied into another URL.
    verify = (ROOT / 'dogrula.html').read_text().replace('<html lang="tr">', '<html lang="en">')
    (target / 'dogrula.html').write_text(verify)
    manifest = json.loads((ROOT / 'site.webmanifest').read_text())
    manifest.update(lang='en', start_url='/en/', description='Deadline and note tracking for lawyers.')
    (target / 'site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')

if __name__ == '__main__':
    main()
