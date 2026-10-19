import numpy as np
import io
import base64
import os 
import zlib

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

        return chunk_status, chunk_name.decode('utf-8', errors='ignore'), chunk_data_readable

    def get_bytes_per_pixel(self, bit_depth, color_type):
        channels_map = {
        0: 1,  # Grayscale (1 канал: Серый)
        2: 3,  # Truecolor / RGB (3 канала: R, G, B)
        3: 1,  # Indexed color / Palette (1 канал: Индекс в палитре)
        4: 2,  # Grayscale + Alpha (2 канала: Серый, Альфа)
        6: 4   # Truecolor + Alpha / RGBA (4 канала: R, G, B, A)
    }
        if color_type not in channels_map:
            raise ValueError(f"Невалидный Color Type: {color_type}")
        
        channels = channels_map[color_type]

        bits_per_pixel = channels * bit_depth

        bytes_per_pixel = (bits_per_pixel + 7) // 8

        return bytes_per_pixel

    def pixel_to_char(self, r, g, b, a):
        grad_str = "@\\$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^` "
        if a < 128:
            return grad_str[-1]

        luma = int(0.299 * r + 0.587 * g + 0.114 * b)

        char_index = (luma * (len(grad_str) - 1)) // 255

        return grad_str[char_index]

    def render_png(self, data:str, ihdr:dict, theme_name:str) -> str:
        width = ihdr["width"]
        length = ihdr["length"]
        theme_name = theme_name.lower()
        themes = {
            "cyberpunk": ("#00060e","#9a9f17","#fee801", "#54c1e6", "#39c4b6")
        }
        if ihdr["CompressionMethod"] == 0:
            decompressed_data = zlib.decompress(data)
        else: return "I DONT KNOW WHAT TO DO WITH THIS!"

        bytes_per_pixel = self.get_bytes_per_pixel(ihdr["bitDepth"], ihdr["ColorType"])

        stride = (width * bytes_per_pixel) + 1

        recon_stride = width * bytes_per_pixel
        recon_buffer = bytearray(width * length * bytes_per_pixel)
        #Дефильтрация
        for y in range(length):
            raw_line_start = y * stride
            filter_type = decompressed_data[raw_line_start]
            raw_pixels = decompressed_data[raw_line_start + 1 : raw_line_start + stride]
            recon_line_start = y * recon_stride
            
            for x_byte in range(recon_stride):
                current_pos = recon_line_start + x_byte
                
                # определение соседей в одномерном байт-массиве
                a = recon_buffer[current_pos - bytes_per_pixel] if x_byte >= bytes_per_pixel else 0
                b = recon_buffer[current_pos - recon_stride] if y > 0 else 0
                c = recon_buffer[current_pos - recon_stride - bytes_per_pixel] if (y > 0 and x_byte >= bytes_per_pixel) else 0

                x = raw_pixels[x_byte]

                if filter_type == 0:    # None
                    recon_value = x
                elif filter_type == 1:  # Sub
                    recon_value = x + a
                elif filter_type == 2:  # Up
                    recon_value = x + b
                elif filter_type == 3:  # Average
                    recon_value = x + (a + b) // 2
                elif filter_type == 4:  # Paeth
                    p = a + b - c
                    pa = abs(p - a)
                    pb = abs(p - b)
                    pc = abs(p - c)
                    
                    if pa <= pb and pa <= pc:
                        pr = a
                    elif pb <= pc:
                        pr = b
                    else:
                        pr = c
                    recon_value = x + pr
                else:
                    raise ValueError(f"Неизвестный тип фильтра: {filter_type}")

                recon_buffer[current_pos] = recon_value & 0xFF
        #Рендер 
        lines_list = []
        for y in range(length):
            line_chars = []
            for x in range(width):
                pixel_index = (y * recon_stride) + (x * bytes_per_pixel)
                
                color_type = ihdr["ColorType"]
                
                # Инициализируем дефолты
                r = g = b = 0
                a = 255

                if color_type == 0:    # Grayscale
                    r = g = b = recon_buffer[pixel_index]
                elif color_type == 2:  # RGB
                    r = recon_buffer[pixel_index]
                    g = recon_buffer[pixel_index + 1]
                    b = recon_buffer[pixel_index + 2]
                elif color_type == 4:  # Grayscale + Alpha
                    r = g = b = recon_buffer[pixel_index]
                    a = recon_buffer[pixel_index + 1]
                elif color_type == 6:  # RGBA
                    r = recon_buffer[pixel_index]
                    g = recon_buffer[pixel_index + 1]
                    b = recon_buffer[pixel_index + 2]
                    a = recon_buffer[pixel_index + 3]
                elif color_type == 3:  # Indexed (Палитра)
                    # Для палитры нужен чанк PLTE, пока ставим заглушку серого
                    r = g = b = recon_buffer[pixel_index]

                char = self.pixel_to_char(r, g, b, a)
                # Дублируем символ, так как консольные шрифты вытянуты по вертикали
                line_chars.append(char * 2)
            
            lines_list.append("".join(line_chars))

        return "\n".join(lines_list)
        
    
    def _processPNG(self):
        nessesary_chunks = dict()
        info_chunks = dict()
        idat_accumulator = b""
        ihdr = b""
        
        with open(self.path, 'rb') as file:
            file.seek(8)
            while True:
                # Читаем длину чанка
                len_bytes = file.read(4)
                if not len_bytes or len(len_bytes) < 4:
                    break  # Защита от бесконечного цикла: файл неожиданно закончился
                    
                chunk_len = int.from_bytes(len_bytes, 'big')
                
                # Читаем имя чанка
                name_bytes = file.read(4)
                if not name_bytes or len(name_bytes) < 4:
                    break  # Защита от бесконечного цикла
                    
                # Читаем данные чанка и CRC
                data = file.read(chunk_len)
                crc = file.read(4)
                
                # Логика распределения чанков
                if name_bytes == b'IHDR':
                    ihdr = data
                    # Для удобства парсим заголовки
                    ihdr_readable = {
                        "width": int.from_bytes(ihdr[0:4], 'big'),
                        "length": int.from_bytes(ihdr[4:8], 'big'),
                        "bitDepth": ihdr[8],
                        "ColorType": ihdr[9],
                        "CompressionMethod": ihdr[10],
                        "FilterMethod": ihdr[11],
                        "InterlaceMethod": ihdr[12]
                    }
                elif name_bytes == b'IDAT':
                    # Накапливаем данные всех IDAT-мешков
                    idat_accumulator += data
                elif name_bytes == b'IEND':
                    break  # Финальный чанк, успешно выходим из цикла
                else:
                    # Все остальные чанки (PLTE, tEXt, gAMA и т.д.) отправляем в chunk_read
                    ch_stat, ch_name, ch_data = self.chunk_read(name_bytes, data, crc)
                    if ch_stat:
                        nessesary_chunks[ch_name] = ch_data
                    else:
                        info_chunks[ch_name] = ch_data

            # Проверяем, что мы нашли всё необходимое перед рендером
            if not ihdr or not idat_accumulator:
                raise ValueError("Поврежденный PNG: отсутствуют чанки IHDR или IDAT")

            # Передаем ПОЛНЫЙ массив сжатых данных в ваш рендер
            idat_render = self.render_png(idat_accumulator, ihdr_readable, "cyberpunk")
        
        return idat_render
    
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
file = os.path.join(file_dir, "cat_PNG115421HALF.png")
# raw_bytes = ImageToASCII.image_read_as_file(file)
work_file = ImageToASCII(file)
print(work_file.path)
print(work_file.file_format)
# print(work_file.process_pipeline())
output = os.path.join(file_dir, "ASCII_cat.txt")
with open(output, "w") as file:
    file.write(work_file.process_pipeline())
# print("Raw Bytes (First 100 chars):", raw_bytes[:100])
# b64_text_string = base64.b64encode(raw_bytes).decode('utf-8')
# print("Safe Text String (First 100 chars):", b64_text_string[:100])
