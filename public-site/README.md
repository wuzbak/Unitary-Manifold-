#!/usr/bin/env python3
"""
Script to compute SRI hashes for CDN scripts after deployment.
Run: python3 TOOLS/compute_sri.py

Then replace the CDN script tags with the output:
  <script src="..." integrity="sha384-HASH" crossorigin="anonymous">
"""
import urllib.request, hashlib, base64

CDNS = {
    "three.js r128": "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",
    "Chart.js 3.9.1": "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js",
}

for name, url in CDNS.items():
    data = urllib.request.urlopen(url).read()
    digest = base64.b64encode(hashlib.sha384(data).digest()).decode()
    print(f'\n# {name}')
    print(f'# URL: {url}')
    print(f'integrity="sha384-{digest}" crossorigin="anonymous"')
