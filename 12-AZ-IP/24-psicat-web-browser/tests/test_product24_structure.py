from __future__ import annotations

import json
import unittest
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]


class Product24StructureTests(unittest.TestCase):
    def test_readme_describes_all_three_surfaces(self) -> None:
        readme = (PRODUCT_ROOT / 'README.md').read_text(encoding='utf-8')
        self.assertIn('Desktop Electron browser shell', readme)
        self.assertIn('Android native-tab browser foundation', readme)
        self.assertIn('Chrome/Edge extension foundation', readme)

    def test_extension_manifest_has_side_panel_and_storage_permissions(self) -> None:
        manifest = json.loads((PRODUCT_ROOT / 'extension' / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(manifest['manifest_version'], 3)
        self.assertIn('sidePanel', manifest['permissions'])
        self.assertEqual(manifest['side_panel']['default_path'], 'sidepanel.html')

    def test_package_json_points_to_electron_entrypoint(self) -> None:
        package_json = json.loads((PRODUCT_ROOT / 'package.json').read_text(encoding='utf-8'))
        self.assertEqual(package_json['main'], 'desktop/main.js')
        self.assertEqual(package_json['scripts']['start'], 'electron .')

    def test_resume_ledger_points_to_readme_entrypoint(self) -> None:
        resume = json.loads((PRODUCT_ROOT / 'SESSION_RESUME.json').read_text(encoding='utf-8'))
        self.assertEqual(resume['product'], 24)
        self.assertTrue(resume['resume_entrypoint'].endswith('/12-AZ-IP/24-psicat-web-browser/README.md'))


if __name__ == '__main__':
    unittest.main()
