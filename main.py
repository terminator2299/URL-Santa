from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from urllib.parse import urlparse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# In-memory history store
recent_checks: List[str] = []


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": None,
        "recent": recent_checks[-5:][::-1]
    })


@app.get("/check", response_class=HTMLResponse)
async def check_url(request: Request, url: str):
    is_valid = is_valid_url(url)
    result = f"✅ {url} is a valid URL." if is_valid else f"❌ {url} is not a valid URL."

    recent_checks.append(result)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result,
        "recent": recent_checks[-5:][::-1]
    })
