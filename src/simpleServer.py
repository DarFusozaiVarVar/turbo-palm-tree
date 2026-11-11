import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values
from urllib.parse import quote_plus
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import TIMESTAMP, DateTime, Integer, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Инициализация среды
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, ".env.secrets")
config = dotenv_values(dotenv_path)
CONFIG_PATH = '/app/config/config.json'
POSTGRES_USER = config["POSTGRES_USER"]
POSTGRES_PASSWORD = config["POSTGRES_PASSWORD"]
POSTGRES_DB = config["POSTGRES_DB"]
POSTGRES_HOST = config.get("POSTGRES_HOST", "db")
POSTGRES_PORT = config.get("POSTGRES_PORT", "5432")
LOG_PATH = config["LOG_PATH"]
CONFIG_PATH = config["CONFIG_PATH"]

POSTGRES_URL = (
    f"postgresql+asyncpg://{quote_plus(POSTGRES_USER)}:{quote_plus(POSTGRES_PASSWORD)}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_PATH)],
)

logger = logging.getLogger(name=__name__)

logger.info("Приложение инициализируется...")

#Инициализация соединения с базой данных
engine = create_async_engine(POSTGRES_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_async_session():
    async with async_session_maker() as session:
        yield session


# ————————————————————

try:
    jinja_env = Environment(
        loader=FileSystemLoader("blogAppTemplates"),
        autoescape=select_autoescape(
            disabled_extensions=("txt",),
            default_for_string=True,
            default=True,
        ),
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

try:
    app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
    logger.info("Статические файлы /scripts успешно смонтированы.")
except Exception as e:
    logger.error(f"Не удалось смонтировать папку scripts: {e}")


# Updates the image of the day status on servers, if Bloom Filter says this picture was already, let another picture take the role
# also don't forget to connect with symbol picture builder to make cool page render effect I guess?
async def imgOfTheday_update(image_path, caption):
    logger.info("Получен запрос на изменение изображения дня.")

    try:
        a = Path(image_path)
        with open(a, "r") as file:
            logger.info("Image file exists and is ready to read")

    except FileNotFoundError:
        logger.info("Image file does not exist")

    if not os.path.exists(image_path):
        logger.error(f"Файл данных {image_path} не найден!")
        raise HTTPException(
            status_code=500, detail="Internal Server Error: Data missing"
        )

    try:
        return

    except Exception as e:
        logger.error(
            f"Ошибка при обработке  запроса на рендер изображения дня: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    logger.info("Получен GET-запрос на маршрут '/'")
    json_path = "BlogListed.json"
    # content = {}

    if not os.path.exists(json_path):
        logger.error(f"Файл данных {json_path} не найден!")
        raise HTTPException(
            status_code=500, detail="Internal Server Error: Data missing"
        )

    try:
        # template = jinja_env.get_template("MotherBase.html")

        with open(json_path, "r", encoding="utf-8") as file:
            blog_dict = json.load(file)

        blocks_count = len(blog_dict.get("BlogListedBlocks", []))
        logger.info(f"Успешно прочитано блоков из JSON: {blocks_count}")

        return templates.TemplateResponse(
            request=request,
            name="MotherBase.html",
            context={
                "blog_block_list": blog_dict["BlogListedBlocks"],
                "current_image": blog_dict.get("ImageOfTheDay", "cat_PNG115421.png"),
                "current_caption": blog_dict.get(
                    "ImageCaption", "This is the picture of the cat!"
                ),
            },
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

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

@app.get("/testUsers")
async def testUsers(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}", exc_info=True)

@app.post("/addUserInfo")
async def addUserTest(session: AsyncSession = Depends(get_async_session)):
    try:
        new_user = User(name="Вова", email="A@a.com")
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}", exc_info=True)

class ga4_sessions(Base):
    __tablename__ = "ga4_sessions"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

@app.post("createPost")
async def create_post(post_data: str):
    try:
        return True
    except Exception as e:
        logger.error(f"Ошибка форматирования данных: {e}", exc_info=True)

# THe coed intended on completion of task 3
# import base64
import urllib.request
import re

ETCD_NODES = [
    "http://localhost:12371",
    "http://localhost:12372",
    "http://localhost:12373",
]

def etcd_post(endpoint: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    last_error = None

    for base_url in ETCD_NODES:
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=2.0) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise HTTPException(status_code=e.code, detail=error_body)
        except Exception as e:
            last_error = e
            continue

    raise HTTPException(
        status_code=503,
        detail=f"Все узлы etcd недоступны. Последняя ошибка: {last_error}",
    )

@app.get("/showNodes")
def show_nodes():
    return etcd_post("/v3/cluster/member/list", {})

@app.post("/addNode") #still under construction need to add init via docker
def add_node(node_name: str = "etcd-a"):
    cluster_data = show_nodes()
    existing_names = {
        member.get("name")
        for member in cluster_data.get("members", [])
        if member.get("name")
    }

    while node_name in existing_names:
        match = re.search(r"^(.*?\W+)(\d+)\s*$", node_name)
        if match:
            prefix = match.group(1)
            number = int(match.group(2))
            node_name = f"{prefix}{number + 1}"
        else:
            node_name = f"{node_name}-1"

    peer_url = f"http://{node_name}:2380"
    payload = {
        "peerURLs": [peer_url],
        "isLearner": True,
    }
    data = json.dumps(payload).encode("utf-8")

    for etcd_url in ETCD_NODES:
        try:
            url = f"{etcd_url}/v3/cluster/member/add"
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=2.0) as response:
                etcd_response = json.loads(response.read().decode("utf-8"))
                return {
                    "assigned_name": node_name,
                    "peer_url": peer_url,
                    "etcd_response": etcd_response,
                }
        except Exception as e:
            logger.warning(f"Не удалось добавить через {etcd_url}: {e}")
            continue

    raise HTTPException(status_code=503, detail="Не удалось подключиться ни к одному узлу etcd")

@app.get("/activeNodes")
def get_active_nodes():
    cluster_data = etcd_post("/v3/cluster/member/list", {})
    members = cluster_data.get("members", [])

    active_nodes = []

    for member in members:
        client_urls = member.get("clientURLs", [])
        if not client_urls:
            continue

        client_url = client_urls[0]
        try:
            health_url = f"{client_url.rstrip('/')}/health"
            req = urllib.request.Request(health_url, method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as response:
                health_data = json.loads(response.read().decode("utf-8"))
                if health_data.get("health") == "true":
                    active_nodes.append({
                        "id": member.get("ID"),
                        "name": member.get("name"),
                        "client_url": client_url,
                        "peer_urls": member.get("peerURLs", []),
                        "is_learner": member.get("isLearner", False),
                    })
        except Exception:
            continue

    return {
        "total_registered": len(members),
        "active_count": len(active_nodes),
        "active_nodes": active_nodes,
    }


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)