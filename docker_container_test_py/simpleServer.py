from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
import json

jinja_env = Environment(
    loader=FileSystemLoader("blogAppTemplates"),
    autoescape=select_autoescape(disabled_extensions=('txt',),
        default_for_string=True,
        default=True,
    )
    )

app = FastAPI()

app.mount("/css", StaticFiles(directory="css"), name="css")

@app.get("/", response_class=HTMLResponse)
async def root():
    template = jinja_env.get_template("MotherBase.html")
    with open("BlogListed.json", "r") as file:
        blog_dict = json.load(file)
    # blog_list = blog_dict
    rendered_html = template.render(blog_block_list = blog_dict["BlogListedBlocks"])
    return rendered_html

@app.get("/blog")
async def blog_block_get(block_id: int):
    return block_id

# if __name__ == "__main__":
#     uvicorn.run("main:app", workers=2)