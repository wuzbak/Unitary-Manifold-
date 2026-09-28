from __future__ import annotations

import json
import unittest
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


class Product25StructureTests(unittest.TestCase):
    def test_readme_describes_mobile_and_training_packet(self) -> None:
        readme = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('desktop and mobile', readme.lower())
        self.assertIn('training packet', readme.lower())
        self.assertIn('/api/psicat', readme)

    def test_manifest_and_resume_ledger_exist(self) -> None:
        manifest = json.loads((PRODUCT_ROOT / 'ui' / 'manifest.webmanifest').read_text(encoding='utf-8'))
        resume = json.loads((PRODUCT_ROOT / 'SESSION_RESUME.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['display'], 'standalone')
        self.assertEqual(resume['product'], 25)
        self.assertTrue(resume['resume_entrypoint'].endswith('/12-AZ-IP/25-psicat-braided-brain/README.md'))

    def test_package_scripts_cover_lint_and_tests(self) -> None:
        package_json = json.loads((PRODUCT_ROOT / 'package.json').read_text(encoding='utf-8'))
        self.assertIn('lint', package_json['scripts'])
        self.assertIn('node --test', package_json['scripts']['test'])


if __name__ == '__main__':
    unittest.main()
