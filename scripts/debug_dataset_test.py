import tempfile
import os
import requests
from PIL import Image

base = 'http://127.0.0.1:5000'
img = Image.new('RGB', (10, 10), (255, 0, 0))
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
    img.save(tmp, 'PNG')
    tmp_path = tmp.name

print('temp image:', tmp_path)
with open(tmp_path, 'rb') as f:
    r = requests.post(f'{base}/api/dataset-detection', files=[('datasetFiles', ('test.png', f, 'image/png'))])
print('status:', r.status_code)
try:
    print('json:', r.json())
except Exception as e:
    print('text:', r.text)

os.remove(tmp_path)
