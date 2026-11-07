# this_file: tests_docs/test_pipeline_frontend.py
"""Verify the actual English browser notices, source maps and output boundary."""
import hashlib
import json
from pathlib import Path
import unittest
import re
from html.parser import HTMLParser
from urllib.parse import unquote

import material

ROOT = Path(__file__).resolve().parents[1]


class IconPaths(HTMLParser):
    """Reuse the reviewed ordered path-d tuple definition, not full SVG geometry."""

    def __init__(self):
        super().__init__()
        self.level = 0
        self.paths = []
        self.tuples = []

    def handle_starttag(self, tag, attrs):
        if tag == 'svg':
            self.level += 1
            self.paths = []
        if tag == 'path' and self.level:
            value = dict(attrs).get('d')
            if value:
                self.paths.append(value)

    def handle_endtag(self, tag):
        if tag == 'svg':
            if self.paths:
                self.tuples.append(tuple(self.paths))
            self.level -= 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def icon_paths(text):
    parser = IconPaths()
    parser.feed(text)
    return set(parser.tuples)


class FrontendPayloadTests(unittest.TestCase):
    def test_every_current_notice_is_exact_in_source_and_generated_payload(self):
        record = json.loads((ROOT / 'src_docs/md/assets/current-frontend-notices.json').read_text())
        self.assertTrue(record['historical_complete_transitive_inventory_remains_false'])
        names = {row['name'] for row in record['components']}
        self.assertTrue({'clipboard', 'tiny-emitter', 'select', 'good-listener', 'delegate', 'escape-html', 'focus-visible', 'rxjs', 'tslib', 'lunr', 'material-design-color', '@mdi/svg', '@fortawesome/fontawesome-free', '@primer/octicons', 'lucide-static'} <= names)
        page = (ROOT / 'src_docs/md/frontend-notices.md').read_text()
        count = 0
        for row in record['components']:
            self.assertTrue(row['source_url'].startswith('https://'))
            for notice in row['notices']:
                count += 1
                data = (ROOT / 'src_docs/md' / notice['path']).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), notice['sha256'])
                self.assertEqual((ROOT / 'docs' / notice['path']).read_bytes(), data)
                self.assertIn(notice['path'], page)
                if row['name'] in ('select', 'good-listener', 'delegate'):
                    self.assertEqual(data.decode().strip(), '## License\n\n[MIT License](http://zenorocha.mit-license.org/) © Zeno Rocha')
        self.assertEqual(count, 25)

    def test_current_source_map_identities_and_exact_embedded_sources_are_retained(self):
        record = json.loads((ROOT / 'src_docs/md/assets/current-frontend-notices.json').read_text())
        for row in record['source_maps']:
            data = (ROOT / 'docs' / row['path']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), row['sha256'])
            source_map = json.loads(data)
            self.assertEqual(source_map['sources'], [s['source'] for s in row['sources']])
            if 'sourcesContent' in source_map:
                self.assertEqual(len(source_map['sourcesContent']), row['sources_count'])
                for body, source in zip(source_map['sourcesContent'], row['sources']):
                    self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), source['sha256'])
                    if 'package' in source:
                        self.assertTrue(source['byte_exact'])
            else:
                self.assertTrue(all(source['sha256'] is None for source in row['sources']))
        self.assertEqual([row['sources_count'] for row in record['source_maps']], [211, 13, 51, 5])

    def test_complete_current_output_contains_no_omitted_helper_or_font_binary(self):
        policy = json.loads((ROOT / 'src_docs/md/assets/english-search-omissions.json').read_text())
        self.assertEqual(len(policy['omitted']), 35)
        for row in policy['omitted']:
            self.assertFalse((ROOT / 'docs' / row['path']).exists())
        for row in policy['retained']:
            self.assertEqual(hashlib.sha256((ROOT / 'docs' / row['path']).read_bytes()).hexdigest(), row['sha256'])
        self.assertFalse([p for p in (ROOT / 'docs').rglob('*') if p.suffix.lower() in ('.woff', '.woff2', '.ttf', '.otf')])

    def test_icon_inventory_matches_actual_html_css_and_installed_path_tuples(self):
        record = json.loads((ROOT / 'src_docs/md/assets/current-frontend-notices.json').read_text())
        scope = record['icons']['path_tuple_scope']
        observed = set()
        for path in (ROOT / 'docs').rglob('*.html'):
            observed.update(icon_paths(path.read_text()))
        css = '\n'.join(path.read_text() for path in (ROOT / 'docs/assets/stylesheets').glob('*.css'))
        for svg in re.findall(r'<svg\b.*?</svg>', unquote(css), re.S):
            observed.update(icon_paths(svg))
        self.assertTrue(observed)
        self.assertEqual(len(observed), scope['observed'])
        icon_root = Path(material.__file__).parent / 'templates/.icons'
        installed = set()
        for family in ('material', 'fontawesome', 'octicons', 'lucide'):
            for path in (icon_root / family).rglob('*.svg'):
                installed.update(icon_paths(path.read_text()))
        self.assertEqual(len(observed & installed), scope['exact_installed_matches'])
        optimized = set()
        for prop in scope['optimized_css_refs'].values():
            values = re.findall(re.escape(prop) + r":url\('data:image/svg\+xml;charset=utf-8,(.*?)'\)", css)
            self.assertEqual(len(values), 1, prop)
            optimized.update(icon_paths(unquote(values[0])))
        self.assertEqual(observed - installed, optimized)
        caret = scope['css_header_attributions']['--md-version-icon']
        values = re.findall(r"--md-version-icon:url\('data:image/svg\+xml;charset=utf-8,(.*?)'\)", css)
        self.assertEqual(len(values), 1)
        svg = unquote(values[0])
        header = re.search(r'<!--!.*?-->', svg, re.S).group(0)
        self.assertEqual(caret['header'], header)
        self.assertIn('Font Awesome Free 7.1.0', header)
        self.assertIn('Copyright 2025 Fonticons, Inc.', header)
        self.assertIn('Icons: CC BY 4.0', header)
        self.assertEqual(caret['installed_icon'], 'fontawesome/solid/caret-down.svg')
        self.assertEqual(icon_paths(svg), icon_paths((icon_root / caret['installed_icon']).read_text()))
        self.assertIs(caret['exact_path_tuple_match'], True)
        self.assertEqual(caret['component'], '@fortawesome/fontawesome-free')
        self.assertEqual(caret['version'], '7.1.0')
        self.assertEqual(caret['icon_terms'], 'CC-BY-4.0')
        self.assertEqual(json.loads((ROOT / 'docs/assets/current-frontend-notices.json').read_text()), record)
