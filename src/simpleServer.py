from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block
import json
import os
import logging
from pathlib import Path

# Инициализация логов

# CONFIG_PATH = '/app/config/config.json'
LOG_PATH = '/app/logs/app.log'

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_PATH)
    ]
)

logger = logging.getLogger(name=__name__)

logger.info("Приложение инициализируется...")


#————————————————————

try:
    jinja_env = Environment(
        loader=FileSystemLoader("blogAppTemplates"),
        autoescape=select_autoescape(disabled_extensions=('txt',),
            default_for_string=True,
            default=True,
        )
        )
    logger.info("Jinja2 environment успешно загружен.")
except Exception as e:
    logger.critical(f"Ошибка инициализации Jinja2: {e}", exc_info=True)

app = FastAPI()

try:
    app.mount("/css", StaticFiles(directory="css"), name="css")
    logger.info("Статические файлы /css успешно смонтированы.")
except Exception as e:
    logger.error(f"Не удалось смонтировать папку css: {e}")

# Will need to improve and add dynamic load of imagew from google, with small caption
@app.get("/imgotday", response_class=HTMLResponse)
async def render_imgOfTheday(image_path, caption):

    logger.info("Получен запрос на рендер изображения дня.")

    try:
        a = Path(image_path)
        with open(a, 'r') as file:
            logger.info("Image file exists and is ready to read")

    except FileNotFoundError:
        logger.info("Image file does not exist")

    context_data = {
        "imageoftheday": "POTD.html",
        "content": {
            "url": image_path,
            "caption": caption
        }
    }

    if not os.path.exists(image_path):
        logger.error(f"Файл данных {image_path} не найден!")
        raise HTTPException(status_code=500, detail="Internal Server Error: Data missing")
    
    try:
        block_content = render_block(
            environment = jinja_env,
            template_name="MotherBase.html",
            block_name="image_day_block",
            **context_data
        )
        return HTMLResponse(content=block_content)

    except Exception as e:
        logger.error(f"Ошибка при обработке  запроса на рендер изображения дня: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") 

@app.get("/", response_class=HTMLResponse)
async def root():
    logger.info("Получен GET-запрос на маршрут '/'")
    json_path = "BlogListed.json"
    
    if not os.path.exists(json_path):
        logger.error(f"Файл данных {json_path} не найден!")
        raise HTTPException(status_code=500, detail="Internal Server Error: Data missing")
    
    try:
        template = jinja_env.get_template("MotherBase.html")
        
        with open(json_path, "r", encoding="utf-8") as file:
            blog_dict = json.load(file)
            
        blocks_count = len(blog_dict.get("BlogListedBlocks", []))
        logger.info(f"Успешно прочитано блоков из JSON: {blocks_count}")

        default_image = "css/cat_PNG115421.png" 
        img_response = await render_imgOfTheday(image_path=default_image, caption="This is the picture of the cat!")

        potd_html_string = img_response.body.decode("utf-8")
        
        html_content = template.render(
            blog_block_list=blog_dict["BlogListedBlocks"],
            potd_pre_rendered=potd_html_string
        )
        logger.info("Шаблон MotherBase.html успешно отрендерен.")
        return HTMLResponse(content = html_content)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке корневого маршрута: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") 

@app.get("/blog")
async def blog_block_get(block_id: int):
    try:
        return block_id
    except Exception as e:
        logger.error(f"Ошибка при обработке маршрута блога: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

# if __name__ == "__main__":
#     uvicorn.run("main:app", workers=2)