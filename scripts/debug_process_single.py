import tempfile
import os
from PIL import Image
from app import process_single_image

img = Image.new('RGB', (10, 10), (255, 0, 0))
with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
    img.save(tmp, 'PNG')
    temp_path = tmp.name

print('temp file', temp_path)
result = process_single_image(temp_path, 'test.png')
print(result)
os.remove(temp_path)
