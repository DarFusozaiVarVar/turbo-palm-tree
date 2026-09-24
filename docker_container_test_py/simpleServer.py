from fastapi import FastAPI
from fastapi.responses import HTMLResponse 
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

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
    blog_list = ["I’m both a bit surprised and unsurprised that it’s been two years since last I posted anything on Hafuboti. I knew that I needed a break, but I had no idea that it would last as long as it has. I’m not even sure that I’ll ever return to posting as regularly as I once…",
                "There are times that an idea tickles me enough that I have to follow it through and make it reality. When our Children’s Librarian Jennifer told me that the new book in Aaron Reynolds’ and Peter Brown’s Creepy Tales! series was Creepy Crayon! and then showed me the cover? I knew what must be done….",
                "Please Note: I failed to take before photos, so you’ll need to imagine those. Yes, this post is the first of my Home Time blog, and I’m aware that this was for my office. That’s okay – this idea works well at home, too. One day, while rearranging my desk, I realized that the mugs I use…"]
    rendered_html = template.render(blog_block_list = blog_list)
    return rendered_html

@app.get("/blog")
async def blog_block_get(block_id: int):
    return block_id

