import numpy as np
import io
import base64
import os 

class ImageToASCII:

    crc_table = []
    crc_table_computed = 0

    def __init__(self, path: str, file_format: str = "unknown"):
        self.path = path
        #breakpoint()
        if "unknown" == file_format.lower():
            self.file_format = self.get_file_format(path)
        else:
            self.file_format = file_format
            
    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value 

    # @path.deleter
    # def path(self):
    #     del self._path

    def get_file_format(self, path = None):
        target_path = path if path is not None else self.path
        with open(target_path, 'rb') as file:
                    header = file.read(12)
        if header.startswith(b'\xff\xd8\xff'):
            return 'JPEG'
        elif header.startswith(b'\x89PNG\x0d\x0a\x1A\x0a'):
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

    def _processJPEG(self):
        return "JPEG processed"
    
    # block for crc table processing of png 
    def make_crc_table():
                crc_table = [None] * 256
                for n in range(0, 256):
                    c = n
                    for k in range(0, 8):
                        if c & 1:
                            c = 0xedb88320 ^ (c >> 1)
                        else:
                            c = c >> 1
                    crc_table[n] = c
                crc_table_computed = 1

    def update_crc(self, crc: int, buf: bytes, len: int):
        c = crc
        if not self.crc_table_computed:
            self.make_crc_table
        for n in range(0, len):
            table_index  = (c ^ buf[n]) & 0xFF
            c = self.crc_table[table_index] ^ (c >> 8)

    def crc(self, buf: bytes, len: int):
        return (self.update_crc(0xFFFFFFFF, buf, len) ^ 0xFFFFFFFF) & 0xFFFFFFFF
    # ————————————————————————————————————————————————————————————————

    def chunk_read(self, chunk_name, chunk, crc):
        chunk_status = False
        if chunk_name == b'PLTE':
            chunk_status = True
            plte = dict()
            for i in range(0, len(chunk), 3):
                plte[f'color{i}'] = [chunk[i], chunk[i+1], chunk[i+2]]
            chunk_data_readable = plte
        else:
            chunk_data_readable = {
                "data" : chunk
            }

        return chunk_status, chunk_name.decode('utf-8'), chunk_data_readable

    def idat_process(self, ihdr):
        return 0
    
    def _processPNG(self):
        nessesary_chunks = dict()
        info_chunks = dict()
        
        with open(self.path, 'rb') as file:
            file.seek(8)
            len = int.from_bytes(file.read(4), 'big')
            name = file.read(4)
            # file.seek(4, io.SEEK_CUR) 
            while b'IHDR' != name:
                data = file.read(len)
                crc = file.read(4)
                ch_stat, ch_name, ch_data = self.chunk_read(name, data, crc)
                if ch_stat:
                    nessesary_chunks[ch_name] = ch_data
                else:
                    info_chunks[ch_name] = ch_data
                len = file.read(4)
                name = file.read(4)
            print(len)
            ihdr = file.read(len)
            print(ihdr)
            ihdr_readable = {
                "width" : int.from_bytes(ihdr[0:4], 'big'),
                "length": int.from_bytes(ihdr[4:8], 'big'),
                "bitDepth": ihdr[8],
                "ColorType": ihdr[9],
                "CompressionMethod": ihdr[10],
                "FilterMethod": ihdr[11],
                "InterlaceMethod": ihdr[12]
            }

            len = int.from_bytes(file.read(4), 'big')
            name = file.read(4)

            while b'IDAT' != name:
                data = file.read(len)
                crc = file.read(4)
                self.chunk_read(name, data, crc)
                len = file.read(4)
                name = file.read(4)
            idat = file.read(4)
            idat.read(len)
            idat_readable = self.idat_process(idat, ihdr)
             
            len = int.from_bytes(file.read(4), 'big')
            name = file.read(4)

            while b'IEND' != name:
                data = file.read(len)
                crc = file.read(4)
                self.chunk_read(name, data, crc)
                len = file.read(4)
                name = file.read(4)
            iend = file.read(4)
        return ihdr_readable
    
    def _processGIF(self):
        return "GIF processed"
    def _processBMP(self):
        return "BMP processed"
    def _processTIFFLE(self):
        return "TIFFLE processed"
    def _processTIFFBE(self):
        return "TIFFBE processed"
    def _processWEBP(self):
        return "WEBP processed"
    def _processICO(self):
        return "ICO processed"

    def process_pipeline(self):
        file_type_action = {
              "JPEG": self._processJPEG,
              "PNG": self._processPNG,
              "GIF": self._processGIF,
              "BMP": self._processBMP,
              "TIFF (Little Endian)": self._processTIFFLE,
              "TIFF (Big Endian)": self._processTIFFBE,
              "WebP": self._processWEBP,
              "ICO": self._processICO
        }

        action = file_type_action.get(self.file_format)
        if not action:
            raise ValueError(f"Неизвестный статус поля: {self.status}")
            
        return action()

    
    
    # def image_read_as_file(f_name: str):
    #     chunk_size = 12 #96 bits
    #     bin_chunk_image = []
    #     with open(f_name, 'rb') as file:
    #         head = file.read(12)
    #         ImageToASCII.get_file_format(head)
    #             # chunk = file.read(chunk_size)
    #             # if not chunk:
    #             #     break
    #             # bin_chunk_image.append(chunk)
    #     return bin_chunk_image


file_dir = os.path.dirname(os.path.abspath(__file__))
file = os.path.join(file_dir, "PNG_transparency_demonstration_1.png")
# raw_bytes = ImageToASCII.image_read_as_file(file)
work_file = ImageToASCII(file)
print(work_file.file_format)
print(work_file.process_pipeline())
# print("Raw Bytes (First 100 chars):", raw_bytes[:100])
# b64_text_string = base64.b64encode(raw_bytes).decode('utf-8')
# print("Safe Text String (First 100 chars):", b64_text_string[:100])
