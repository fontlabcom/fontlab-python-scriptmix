# this_file: tests_docs/test_pipeline_site.py
"""Check the actual generated payload, routes and public source boundaries."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'
PREFIX = '/fontlab-python-scriptmix/'
SOURCE = ROOT / 'src_docs' / 'md'
EXCLUDED = tuple(
    line.removesuffix('**')
    for line in yaml.safe_load((ROOT / 'src_docs' / 'mkdocs.yml').read_text())['exclude_docs'].split()
)
# Every authored page, derived from the Markdown source tree minus mkdocs' exclude_docs.
PAGES = sorted(
    str(path.relative_to(SOURCE).with_suffix('.html'))
    for path in SOURCE.rglob('*.md')
    if not str(path.relative_to(SOURCE)).startswith(EXCLUDED)
)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.links = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    def test_all_generated_internal_links_and_fragments_resolve(self):
        for path in SITE.rglob('*.html'):
            for link in Page(path.read_text()).links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path)
                if target.startswith('/'):
                    self.assertTrue(target.startswith(PREFIX), (path, link))
                    dest = SITE / target.removeprefix(PREFIX)
                else:
                    dest = path.parent / target if target else path
                if dest.is_dir():
                    dest = dest / 'index.html'
                self.assertTrue(dest.is_file(), (path, link, dest))
                self.assertTrue(dest.resolve().is_relative_to(SITE.resolve()), link)
                if url.fragment and dest.suffix == '.html':
                    self.assertIn(unquote(url.fragment), Page(dest.read_text()).ids, (path, link))

    def test_built_pages_are_exactly_the_authored_pages(self):
        built = sorted(str(path.relative_to(SITE)) for path in SITE.rglob('*.html') if path.name != '404.html')
        self.assertEqual(built, PAGES)

    def test_pages_have_light_menu_footer_local_search_and_correct_canonical(self):
        for route in PAGES:
            page = Page((SITE / route).read_text())
            with self.subTest(route=route):
                self.assertEqual([attrs.get('mode') for tag, attrs in page.tags if tag == 'fontlab-menu'], ['light'])
                self.assertEqual([attrs.get('mode') for tag, attrs in page.tags if tag == 'fontlab-footer'], ['light'])
                self.assertEqual([attrs.get('data-md-color-scheme') for tag, attrs in page.tags if tag == 'body'], ['default'])
                search = [attrs for tag, attrs in page.tags if attrs.get('data-md-component') == 'search-query']
                self.assertEqual(len(search), 1)
                self.assertFalse(any(attrs.get('data-md-component') == 'palette' for _, attrs in page.tags))
                canonical = [attrs['href'] for tag, attrs in page.tags if attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://code.fontlab.com/fontlab-python-scriptmix/' + route])

    def test_search_indexes_every_authored_page(self):
        search = json.loads((SITE / 'search/search_index.json').read_text())
        locations = {row['location'].split('#')[0] for row in search['docs']}
        self.assertEqual(locations, {'scripts/font-ui-lab/ufo-roundtrip-inspector.html', 'scripts/font-ui-lab/master-compatibility-browser.html', 'scripts/masters/transform-background.html', 'scripts/proof/random-uppercase-nontext.html', 'scripts/font-ui-lab/representation-and-notification-explorer.html', 'scripts/reports/unicode-coverage.html', 'scripts/font-info/font-metrics.html', 'plugins.html', 'scripts/cleanup/start-from-scratch.html', 'tags.html', 'scripts/contours/node-editor.html', 'scripts/proof/real-english-text.html', 'scripts/anchors/center-horizontally.html', 'scripts/anchors/derive-anchors-from-components.html', 'scripts/components/make-lower-unicase.html', 'scripts/reports/dangerous-offcurves.html', 'scripts/reports/close-but-no-cigar.html', 'scripts/proof/glyphs-surrounded-by-h.html', 'scripts/metrics/spacing-studio.html', 'scripts/anchors/mirror-across-masters.html', 'scripts/components/decompose-serif-components.html', 'scripts/contours/curve-editor.html', 'scripts/anchors/duplicates-finder.html', 'scripts/cleanup/index.html', 'background-cleaning.html', 'backlog.html', 'scripts/guides/suggest-zones-from-overshoots.html', 'scripts/index.html', 'topics.html', 'scripts/components/component-graph.html', 'retirement-decisions.html', 'scripts/proof/highest-lowest-glyphs.html', 'scripts/masters/sync-sidebearings.html', 'scripts/cleanup/select-unreferenced-glyphs.html', 'scripts/names/index.html', 'scripts/reports/smallcap-consistency.html', 'scripts/reports/nodes-near-zones.html', 'scripts/components/decompose-named-components.html', 'scripts/anchors/copy-anchors-between-fonts.html', 'scripts/reports/case-coverage.html', 'scripts/font-ui-lab/anchor-and-component-inspector.html', 'scripts/kerning/kerning-studio.html', 'scripts/guides/font-guides-panel.html', 'scripts/metrics/vertical-metrics.html', 'scripts/metrics/index.html', 'scripts/contours/outline-compatibility.html', 'scripts/anchors/add-anchors-from-file.html', 'scripts/font-info/font-identity.html', 'scripts/font-info/index.html', 'scripts/reports/report-glyph-set-differences.html', 'scripts/proof/glyphs-surrounded-by-nnonn.html', 'scripts/proof/hoefler-uppercase.html', 'scripts/components/copy-offsets-between-masters.html', 'scripts/anchors/duplicate-anchor-rings.html', 'raise-ascender.html', 'scripts/font-ui-lab/designspace-source-comparison.html', 'scripts/masters/index.html', 'scripts/masters/set-intermediate-layer.html', 'scripts/proof/random-uppercase-words.html', 'scripts/proof/text-filter.html', 'scripts/font-ui-lab/glyph-browser-and-metrics.html', 'frontend-notices.html', 'scripts/reports/master-structure-audit.html', 'scripts/components/unlock-lock.html', 'scripts/proof/show-all-layers.html', 'scripts/masters/master-switcher.html', 'scripts/anchors/rename-bulk.html', 'scripts/proof/index.html', 'scripts/reports/live-glyph-info.html', 'scripts/contours/align-and-nudge.html', 'scripts/masters/master-twins.html', 'scripts/reports/glyph-table-csv.html', 'scripts/components/missing-bases.html', 'scripts/anchors/cloud-view.html', 'scripts/proof/glyph-grid.html', 'scripts/reports/report-composite-differences.html', 'scripts/features/feature-explorer.html', 'scripts/contours/hint-tools.html', 'guides/text-holder.html', 'scripts/font-ui-lab/master-width-comparison.html', 'scripts/guides/grid-generator.html', 'scripts/guides/guide-list-editor.html', 'scripts/masters/select-different-colour.html', 'scripts/guides/metric-reference-lines.html', 'scripts/anchors/mark-attachment-preview.html', 'scripts/anchors/auto-cursive-attachment-add-anchors.html', 'scripts/components/index.html', 'scripts/features/index.html', 'scripts/masters/width-chart.html', 'install.html', 'scripts/proof/glyphs-surrounded-by-hhohh.html', 'scripts/components/dump-component-recipes.html', 'scripts/kerning/kerning-proof.html', 'guides/pre-integration.html', 'scripts/cleanup/clear-all-layer-backgrounds.html', 'scripts/components/build-from-recipes.html', 'scripts/contours/index.html', 'scripts/font-ui-lab/kerning-group-explorer.html', 'scripts/proof/text-by-master.html', 'scripts/components/nested-finder.html', 'scripts/reports/empty-glyphs.html', 'scripts/anchors/optical-center.html', 'scripts/contours/outline-doctor.html', 'scripts/names/glyph-identity.html', 'scripts/anchors/delete-by-name.html', 'scripts/proof/word-finder.html', 'scripts/proof/character-map.html', 'scripts/guides/clear-glyph-guides.html', 'cross-font-reports.html', 'scripts/reports/metric-reports.html', 'scripts/components/align-by-anchor.html', 'scripts/utilities/text-holder.html', 'scripts/components/where-used.html', 'scripts/kerning/index.html', 'scripts/masters/master-text-comparison.html', 'scripts/masters/selection-layer-navigator.html', 'scripts/components/compatibility.html', 'scripts/components/set-default-figures.html', 'scripts/proof/bracket-layers-and-components.html', 'scripts/proof/real-spanish-text.html', 'scripts/utilities/index.html', 'scripts/masters/common-glyphs.html', 'scripts/font-ui-lab/open-fonts-and-master-overview.html', 'scripts/reports/font-overview.html', 'scripts/utilities/reference-image-viewer-app.html', 'use.html', 'scripts/components/replace-reference.html', 'scripts/reports/bracket-layers-and-components.html', 'scripts/components/decompose.html', 'scripts/masters/compatibility-check.html', 'near-miss-report.html', 'scripts/masters/restore-backup-layer.html', 'scripts/anchors/index.html', 'scripts/masters/show-all-layers.html', 'scripts/reports/nodes-near-zones-app.html', 'scripts/anchors/round-to-grid.html', 'scripts/proof/glyphs-between-oldstyle-figures.html', 'scripts/reports/event-log.html', 'scripts/cleanup/empty-layers.html', 'scripts/anchors/snap-to-metrics.html', 'scripts/masters/glyph-weight-chart.html', 'licenses.html', 'scripts/components/set-component-locations.html', 'scripts/font-info/encoding-and-order.html', 'scripts/proof/glyphs-between-uppercase.html', 'scripts/masters/layer-cleanup.html', 'scripts/proof/glyphs-between-lining-figures.html', 'scripts/features/feature-authoring.html', 'scripts/features/nastaliq-connections.html', 'scripts/proof/kernking.html', 'scripts/utilities/magic-remover.html', 'scripts/names/glyph-labels.html', 'scripts/names/character-consistency.html', 'scripts/masters/reorder-shapes.html', 'scripts/proof/glyphs-between-lowercase.html', 'scripts/reports/dump-to-svg-path-commands.html', 'scripts/metrics/advance-widths.html', 'scripts/reports/font-revision-comparison.html', 'scripts/font-ui-lab/interpolation-preview.html', 'scripts/proof/waterfall.html', 'scripts/utilities/find-font-files.html', 'scripts/masters/duplicate-current-layer.html', 'scripts/masters/overview.html', 'scripts/proof/kernsym.html', 'scripts/cleanup/delete-stickers.html', 'scripts/font-ui-lab/feature-source-and-proof.html', 'scripts/reports/open-contours-app.html', 'scripts/contours/transform-studio.html', 'scripts/masters/display-next-layer.html', 'scripts/masters/interpolation-preview.html', 'scripts/font-ui-lab/index.html', 'scripts/proof/glyphs-surrounded-by-i.html', 'scripts/proof/random-lowercase-words.html', 'scripts/masters/use-layer-as-master.html', 'scripts/reports/compare-open-font-revisions.html', 'scripts/reports/categories-to-xml-lib-key.html', 'scripts/proof/tallest-and-shortest.html', 'scripts/anchors/copy-anchors-from-glyph.html', 'scripts/masters/italic-angle.html', 'scripts/guides/perpendicular-guides.html', 'scripts/guides/index.html', 'scripts/kerning/kerning-batch.html', 'scripts/contours/derived-glyphs.html', 'scripts/proof/hoefler-lowercase.html', 'scripts/components/count-badges.html', 'scripts/proof/random-numbers.html', 'scripts/font-ui-lab/detached-transform-preview.html', 'scripts/proof/random-title-nontext.html', 'scripts/contours/shape-generators.html', 'scripts/anchors/place-from-bounds.html', 'scripts/reports/vertical-metrics-reporter.html', 'contribute.html', 'scripts/reports/geometry-audit.html', 'scripts/reports/sidebearing-direction-marker.html', 'scripts/metrics/zero-width-marks.html', 'scripts/proof/random-lowercase-nontext.html', 'scripts/reports/master-node-compatibility-report.html', 'scripts/reports/point-counter.html', 'scripts/utilities/reference-image-viewer.html', 'scripts/anchors/auto-cursive-attachment-get-sample.html', 'scripts/font-ui-lab/batch-ufo-recipe-workbench.html', 'scripts/guides/copy-guides-between-masters.html', 'scripts/masters/deliver-glyphs.html', 'scripts/contours/tglyph-window.html', 'scripts/anchors/compatibility-report.html', 'index.html', 'scripts/reports/font-audit.html', 'scripts/reports/open-contours.html', 'scripts/contours/contour-selection.html', 'scripts/masters/selection-to-all-backgrounds.html', 'scripts/masters/display-previous-layer.html', 'scripts/reports/label-statistics.html', 'scripts/names/glyph-browser.html', 'scripts/masters/copy-layer-between-masters.html', 'scripts/masters/copy-outline-to-mask.html', 'scripts/reports/why-you-not-compatible.html', 'scripts/reports/index.html', 'scripts/font-ui-lab/node-counts-across-masters.html', 'scripts/anchors/copy-myanmar-anchors.html', 'scripts/font-ui-lab/kerning-proof-workbench.html', 'scripts/font-ui-lab/tabular-width-audit.html', 'scripts/kerning/kerning-browser.html', 'scripts/font-ui-lab/font-info-and-vertical-metrics.html', 'scripts/proof/context-proof.html', 'scripts/font-ui-lab/unicode-and-glyph-order-explorer.html', 'scripts/anchors/remove-extraneous-mark-anchors.html', 'scripts/reports/point-counter-master-layers.html', 'scripts/cleanup/clear-master-backgrounds.html', 'scripts/components/report.html', 'scripts/proof/random-title-words.html'})
        text = " ".join(row["text"] for row in search["docs"])
        for term in ['Text Holder', '261', '350', '130', '68', 'Close But No Cigar']:
            self.assertIn(term, text)

    def test_attribution_downloads_are_exact_and_no_private_payload_is_published(self):
        for name in ['LICENSE', 'NOTICE']:
            self.assertEqual((ROOT / name).read_bytes(), (SITE / 'assets' / name).read_bytes())
        self.assertTrue((SITE / '.nojekyll').is_file())
        private_markers = (b'/Users/', b'/Volumes/', b'/private/', b'ghp_', b'github_pat_', b'-----BEGIN PRIVATE KEY-----')
        sources = [path.read_bytes() for folder in ('src', 'Scripts', 'glyphs', 'examples') if (ROOT / folder).is_dir() for path in (ROOT / folder).rglob('*.py')]
        for path in SITE.rglob('*'):
            if path.is_file():
                self.assertNotIn('.DS_Store', path.parts)
                self.assertNotIn(path.suffix, ('.py', '.pyi', '.vfpy', '.whl', '.zip'))
                payload = path.read_bytes()
                for marker in private_markers:
                    self.assertFalse(marker in payload.replace(b"/private/var", b""), (path, marker))
                for source in sources:
                    if len(source) > 80:
                        self.assertFalse(source in payload, path)

    def test_workflow_builds_every_main_push_and_requalifies_immutable_output(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        events = workflow.get('on', workflow.get(True))
        self.assertEqual(events['push'], {'branches': ['main']})
        self.assertNotIn('concurrency', workflow)
        build = workflow['jobs']['build']
        verify = workflow['jobs']['qualify-generated-output']
        self.assertNotIn('concurrency', build)
        self.assertEqual(verify['needs'], 'build')
        self.assertEqual(build['outputs']['epoch'], '${{ steps.epoch.outputs.value }}')
        for job, epoch in ((build, '${{ steps.epoch.outputs.value }}'), (verify, '${{ needs.build.outputs.epoch }}')):
            build_step = next(s for s in job['steps'] if s.get('run') == 'sh src_docs/build.sh')
            self.assertEqual(build_step['env']['SOURCE_DATE_EPOCH'], epoch)
        self.assertEqual(verify['steps'][0]['with']['ref'], '${{ needs.build.outputs.sha }}')
        self.assertEqual(verify['permissions'], {'contents': 'read', 'pages': 'write'})
        for job in (build, verify):
            runs = '\n'.join(step.get('run', '') for step in job['steps'])
            self.assertIn('sh src_docs/build.sh', runs)
            self.assertIn('--require-hashes -r src_docs/requirements.txt', runs)
        self.assertIn('git diff --exit-code HEAD -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertIn('git ls-files --others -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertFalse(any('publish.sh' in s.get('run', '') for s in verify['steps']))

    def test_public_request_uses_qualified_output_and_avoids_redundant_push_build(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        job = workflow['jobs']['qualify-generated-output']
        request = next(s for s in job['steps'] if s.get('name') == 'Request branch-source Pages build')
        self.assertEqual(request['if'], "github.event_name == 'workflow_dispatch' || needs.build.outputs.sha != github.sha")
        self.assertEqual(request['env']['OUTPUT_SHA'], '${{ needs.build.outputs.sha }}')
        self.assertEqual(request['run'], 'sh src_docs/request-pages.sh "$OUTPUT_SHA"')

    def test_complete_content_and_source_identity(self):
        import hashlib
        import ast
        from urllib.parse import quote
        menus = sorted((ROOT / 'Scripts').glob('*/*.py'))
        self.assertEqual(len(menus), 197)
        pages = [p for p in (ROOT / 'src_docs/md/scripts').glob('*/*.md') if p.name != 'index.md']
        self.assertEqual(len(pages), 197)
        for source in menus:
            data = source.read_bytes()
            description = ast.get_docstring(ast.parse(data))
            self.assertTrue(description and len(description.strip()) > 20, source)
            sha = hashlib.sha256(data).hexdigest()
            matches = [p for p in pages if sha in p.read_text()]
            self.assertEqual(len(matches), 1, source)
            text = matches[0].read_text()
            self.assertIn(description, text)
            relative = source.relative_to(ROOT).as_posix()
            if ('Immutable source link pending a reviewed containing commit.' in text
                    or 'Source link awaits a reviewed commit containing this new menu script.' in text):
                # Candidate launchers carry no immutable link until a reviewed commit contains them.
                self.assertNotRegex(text, r'/blob/[0-9a-f]{40}/')
                continue
            self.assertIn(quote(relative, safe='/'), text)
            self.assertRegex(text, r'/blob/[0-9a-f]{40}/')
            self.assertNotIn('codeinclude', text)
