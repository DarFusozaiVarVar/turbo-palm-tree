import numpy as np
import base64
import os 

class image_to_ASCII:

    def __init__(self, path: str, file_format: str = "unknown"):
        self.path = path
        self.file_format = file_format
        if "unknown" == file_format:
            self.get_file_format
            
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._attribute = value 

    # @path.deleter
    # def path(self):
    #     del self._path

    def get_file_format(self):
        with open(self.path, 'rb') as file:
                    header = file.read(12)
                    image_to_ASCII.get_file_format(header)
        if header.startswith(b'\xff\xd8\xff'):
            return 'JPEG'
        elif header.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'PNG'
        elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
            return 'GIF'
        elif header.startswith(b'BM'):
            return 'BMP'
        elif header.startswith(b'II*\x00'):
            return 'TIFF (Little Endian)'
        elif header.startswith(b'MM\x00*'):
            return 'TIFF (Big Endian)'
        elif header.startswith(b'RIFF') and header[8:12] == b'WEBP':
            return 'WebP'
        elif header.startswith(b'\x00\x00\x01\x00'):
            return 'ICO'
        
        return 'Unknown'

    # def image_read_as_file(f_name: str):
    #     chunk_size = 12 #96 bits
    #     bin_chunk_image = []
    #     with open(f_name, 'rb') as file:
    #         head = file.read(12)
    #         image_to_ASCII.get_file_format(head)
    #             # chunk = file.read(chunk_size)
    #             # if not chunk:
    #             #     break
    #             # bin_chunk_image.append(chunk)
    #     return bin_chunk_image


file_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(file_dir, "cat_test_image.png")
# raw_bytes = image_to_ASCII.image_read_as_file(file)
work_file = image_to_ASCII(file)
print(work_file.file_format)
# print("Raw Bytes (First 100 chars):", raw_bytes[:100])
# b64_text_string = base64.b64encode(raw_bytes).decode('utf-8')
# print("Safe Text String (First 100 chars):", b64_text_string[:100])
