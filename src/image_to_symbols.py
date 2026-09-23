import numpy as np
import base64
import os 

def image_read_as_file(f_name: str):
    with open(f_name, 'rb') as image:
        image_text = image.read()
    return image_text

file_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(file_dir, "cat_test_image.png")
raw_bytes = image_read_as_file(file)
b64_text_string = base64.b64encode(raw_bytes).decode('utf-8')
print("Safe Text String (First 100 chars):", b64_text_string[:100])
