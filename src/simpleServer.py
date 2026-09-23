from fastapi import FastAPI
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

jinja_env = Environment(
    loader=FileSystemLoader("blogAppTemplates"),
    autoescape=select_autoescape()
)

app = FastAPI()


@app.get("/")
async def root():
    template = jinja_env.get_template("MotherBase.html")
    return {"message": "Hello World"}

@app.get("/")
async def blog_block_get(block_id: int):
    return block_id

