"""
Simple test script to upload image files to the local `/dataset` endpoint.
Usage:
    python scripts/test_dataset.py path/to/img1.jpg path/to/img2.jpg

Requires: requests (pip install requests)
"""

import sys
import requests
from pathlib import Path


def main(paths):
    if not paths:
        print("Usage: python scripts/test_dataset.py file1 [file2 ...]")
        return

    url = 'http://127.0.0.1:5000/dataset'
    files = []
    opened = []
    try:
        for p in paths:
            fp = Path(p)
            if not fp.exists():
                print(f"File not found: {p}")
                return
            f = open(fp, 'rb')
            opened.append(f)
            files.append(('datasetFiles', (fp.name, f, 'application/octet-stream')))

        print(f"Uploading {len(files)} files to {url}...")
        resp = requests.post(url, files=files)
        print('Status:', resp.status_code)
        try:
            print(resp.json())
        except Exception:
            print(resp.text)
    finally:
        for f in opened:
            try:
                f.close()
            except Exception:
                pass


if __name__ == '__main__':
    main(sys.argv[1:])
