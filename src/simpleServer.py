from fastapi import FastAPI, HTTPException, Request
import uvicorn
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_fragments import render_block
from markupsafe import Markup, escape
import json
import os
import logging
from pathlib import Path
import anyio

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
    templates = Jinja2Templates(env=jinja_env)
    logger.info("Jinja2 environment успешно загружен.")
except Exception as e:
    logger.critical(f"Ошибка инициализации Jinja2: {e}", exc_info=True)

app = FastAPI()

try:
    app.mount("/css", StaticFiles(directory="css"), name="css")
    logger.info("Статические файлы /css успешно смонтированы.")
except Exception as e:
    logger.error(f"Не удалось смонтировать папку css: {e}")

# Updates the image of the day status on servers, if Bloom Filter says this picture was already, let another picture take the role
# also don't forget to connect with symbol picture builder to make cool page render effect I guess?
async def imgOfTheday_update(image_path, caption):
    logger.info("Получен запрос на изменение изображения дня.")

    try:
        a = Path(image_path)
        with open(a, 'r') as file:
            logger.info("Image file exists and is ready to read")

    except FileNotFoundError:
        logger.info("Image file does not exist")


    if not os.path.exists(image_path):
        logger.error(f"Файл данных {image_path} не найден!")
        raise HTTPException(status_code=500, detail="Internal Server Error: Data missing")
    
    try:
        return None

    except Exception as e:
        logger.error(f"Ошибка при обработке  запроса на рендер изображения дня: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error") 

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info("Получен GET-запрос на маршрут '/'")
    json_path = "BlogListed.json"
    content = {}
    
    if not os.path.exists(json_path):
        logger.error(f"Файл данных {json_path} не найден!")
        raise HTTPException(status_code=500, detail="Internal Server Error: Data missing")
    
    try:
        #template = jinja_env.get_template("MotherBase.html")
        
        with open(json_path, "r", encoding="utf-8") as file:
            blog_dict = json.load(file)
            
        blocks_count = len(blog_dict.get("BlogListedBlocks", []))
        logger.info(f"Успешно прочитано блоков из JSON: {blocks_count}")

        return templates.TemplateResponse(request=request, name="MotherBase.html", 
                                          context={"blog_block_list": blog_dict["BlogListedBlocks"],
                                                   "current_image": blog_dict.get("ImageOfTheDay", "cat_PNG115421.png"),
                                                    "current_caption": blog_dict.get("ImageCaption", "This is the picture of the cat!")
                                                    }
                                            )
        
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