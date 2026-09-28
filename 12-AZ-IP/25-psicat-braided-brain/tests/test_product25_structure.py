from __future__ import annotations

import json
import unittest
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


class Product25StructureTests(unittest.TestCase):
    def test_readme_describes_offline_and_save_bundle(self) -> None:
        readme = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('desktop and mobile', readme.lower())
        self.assertIn('save bundle', readme.lower())
        self.assertIn('offline', readme.lower())
        self.assertIn('/api/psicat', readme)

    def test_manifest_resume_and_service_worker_exist(self) -> None:
        manifest = json.loads((PRODUCT_ROOT / 'ui' / 'manifest.webmanifest').read_text(encoding='utf-8'))
        resume = json.loads((PRODUCT_ROOT / 'SESSION_RESUME.json').read_text(encoding='utf-8'))
        service_worker = (PRODUCT_ROOT / 'sw.js').read_text(encoding='utf-8')
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(resume['product'], 25)
        self.assertTrue(resume['resume_entrypoint'].endswith('/12-AZ-IP/25-psicat-braided-brain/README.md'))
        self.assertIn('CACHE_NAME', service_worker)

    def test_package_scripts_cover_lint_and_tests(self) -> None:
        package_json = json.loads((PRODUCT_ROOT / 'package.json').read_text(encoding='utf-8'))
        self.assertIn('lint', package_json['scripts'])
        self.assertIn('node --test', package_json['scripts']['test'])
        self.assertIn('sw.js', package_json['scripts']['lint'])


if __name__ == '__main__':
    unittest.main()
