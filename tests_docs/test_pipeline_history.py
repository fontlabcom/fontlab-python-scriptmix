# this_file: tests_docs/test_pipeline_history.py
"""Exercise real shallow Git history without changing the source repository."""
import hashlib
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from urllib.parse import quote

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = "src_docs/build.py"
OUTPUT = "src_docs/md/scripts"
COUNT = 275


class SourceHistoryTests(unittest.TestCase):
    def test_both_jobs_resolve_all_source_links_after_docs_only_shallow_children(self):
        names = subprocess.check_output(['git', 'rev-parse', '--local-env-vars'], text=True).splitlines()
        env = {key: value for key, value in os.environ.items() if key not in names}
        env.update(GIT_AUTHOR_NAME='History fixture', GIT_AUTHOR_EMAIL='fixture@example.invalid',
                   GIT_COMMITTER_NAME='History fixture', GIT_COMMITTER_EMAIL='fixture@example.invalid')
        spec = importlib.util.spec_from_file_location('site_catalogue', ROOT / GENERATOR)
        generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator)
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        with tempfile.TemporaryDirectory() as directory:
            full = Path(directory) / 'full'
            subprocess.run(['git', 'clone', '--quiet', '--no-hardlinks', str(ROOT), str(full)], env=env, check=True)
            def git(root, *args):
                return subprocess.check_output(['git', '-C', str(root), *args], env=env, text=True).strip()
            base = git(ROOT, 'rev-parse', 'HEAD')
            git(full, 'checkout', '--quiet', '--detach', base)
            revision = git(full, 'log', '-1', '--format=%H', '--', 'Scripts')
            for number in (1, 2):
                (full / 'history-fixture.txt').write_text(str(number))
                git(full, 'add', 'history-fixture.txt')
                git(full, 'commit', '--quiet', '-m', 'Owned docs-only history fixture')
            generator.catalogue(full)
            expected = {p.relative_to(full / OUTPUT).as_posix(): p.read_bytes()
                        for p in (full / OUTPUT).rglob('*.md')}
            menus = sorted((full / 'Scripts').glob('*/*.py'))
            self.assertEqual(len(menus), COUNT)
            for menu in menus:
                relative = menu.relative_to(full).as_posix()
                self.assertEqual(subprocess.check_output(['git', '-C', str(full), 'show', revision + ':' + relative], env=env), menu.read_bytes())
                digest = hashlib.sha256(menu.read_bytes()).hexdigest()
                pages = [data.decode() for data in expected.values() if digest in data.decode()]
                self.assertEqual(len(pages), 1)
                self.assertIn('/blob/' + revision + '/' + quote(relative, safe='/'), pages[0])
            for job_name, depth in [('build', 1), ('qualify-generated-output', 2)]:
                with self.subTest(job=job_name):
                    shallow = Path(directory) / job_name
                    subprocess.run(['git', 'clone', '--quiet', '--depth', str(depth), full.as_uri(), str(shallow)], env=env, check=True)
                    self.assertEqual(git(shallow, 'rev-parse', '--is-shallow-repository'), 'true')
                    self.assertNotEqual(git(shallow, 'log', '-1', '--format=%H', '--', 'Scripts'), revision)
                    generator.catalogue(shallow)
                    before = {p.relative_to(shallow / OUTPUT).as_posix(): p.read_bytes() for p in (shallow / OUTPUT).rglob('*.md')}
                    self.assertNotEqual(before, expected, 'Fixture must reproduce the actual shallow-link defect')
                    checkout = workflow['jobs'][job_name]['steps'][0]
                    self.assertEqual(checkout['with'].get('fetch-depth', 1), 0, 'Both jobs need complete relevant history')
                    git(shallow, 'fetch', '--quiet', '--unshallow', 'origin')
                    self.assertEqual(git(shallow, 'rev-parse', '--is-shallow-repository'), 'false')
                    self.assertEqual(git(shallow, 'log', '-1', '--format=%H', '--', 'Scripts'), revision)
                    generator.catalogue(shallow)
                    actual = {p.relative_to(shallow / OUTPUT).as_posix(): p.read_bytes() for p in (shallow / OUTPUT).rglob('*.md')}
                    self.assertEqual(actual, expected)
