import numpy as np
import base64
import os 

def image_read_as_file(f_name: str):
    chunk_size = 12 #96 bits
    bin_chunk_image = []
    with open(f_name, 'rb') as image:

        while True:
            chunk = image.read(chunk_size)
            if not chunk:
                break
            bin_chunk_image.append(chunk)
    return bin_chunk_image

file_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(file_dir, "cat_test_image.png")
raw_bytes = image_read_as_file(file)
print(raw_bytes)
# print("Raw Bytes (First 100 chars):", raw_bytes[:100])
# b64_text_string = base64.b64encode(raw_bytes).decode('utf-8')
# print("Safe Text String (First 100 chars):", b64_text_string[:100])
