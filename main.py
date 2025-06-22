from fastapi import FastAPI, Query, Request, Form, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import validators
import os
import secrets
import logging
from typing import Optional
from pydantic import BaseModel
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from config import users_collection, urls_collection
from utils import generate_short_code, generate_qr_code

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add session middleware
# In a production environment, this secret key should be loaded from a secure source.
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Optional: Serve static files if needed in the future
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class URLData(BaseModel):
    url: str
    password: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = request.session.get("user")
    # The template will receive user, short_url, and qr_code_b64.
    # Initially, short_url and qr_code_b64 are None.
    return templates.TemplateResponse("index.html", {"request": request, "user": user, "short_url": None, "qr_code_b64": None})

@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {"status": "healthy", "message": "URL Santa is running"}

@app.get("/check", response_class=JSONResponse)
async def check_url(url: str = Query(...)):
    try:
        logger.info(f"Checking URL: {url}")
        is_valid = validators.url(url)
        logger.info(f"URL validation result: {is_valid}")
        return {"valid": is_valid}
    except Exception as e:
        logger.error(f"Error checking URL {url}: {str(e)}")
        return {"valid": False, "error": str(e)}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

@app.post("/shorten", response_class=JSONResponse)
async def shorten_url(request: Request, data: URLData):
    user = request.session.get("user")
    long_url = data.url
    password = data.password

    if not validators.url(long_url):
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    owner_username = user.get("username") if user else "guest"
    
    query = {"long_url": long_url, "owner": owner_username}
    existing_url = await urls_collection.find_one(query)
    
    if existing_url:
        short_code = existing_url["short_code"]
    else:
        short_code = generate_short_code()
        await urls_collection.insert_one({
            "long_url": long_url,
            "short_code": short_code,
            "owner": owner_username,
            "password": password
        })

    short_url = f"{request.url.scheme}://{request.url.netloc}/{short_code}"
    qr_code_b64 = generate_qr_code(short_url)

    return {
        "short_url": short_url,
        "qr_code_b64": qr_code_b64,
    }

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), password: str = Form(...)):
    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Username already exists. Please choose another."
        })
    
    hashed_password = get_password_hash(password)
    await users_collection.insert_one({"username": username, "password": hashed_password})
    
    return RedirectResponse("/login?registered=true", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, registered: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "registered": registered})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_doc = await users_collection.find_one({"username": username})
    
    if not user_doc or not verify_password(password, user_doc["password"]):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password."}
        )
    
    request.session["user"] = {"username": username}
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

@app.post("/verify-password/{short_code}", response_class=JSONResponse)
async def verify_short_url_password(short_code: str, request: Request):
    form_data = await request.json()
    password = form_data.get("password")
    
    url_mapping = await urls_collection.find_one({"short_code": short_code})
    if not url_mapping:
        raise HTTPException(status_code=404, detail="URL not found")

    if url_mapping.get("password") and url_mapping.get("password") == password:
        return {"url": url_mapping["long_url"]}
    
    raise HTTPException(status_code=401, detail="Invalid password")

# This must be the last route
@app.get("/{short_code}")
async def redirect_to_long_url(request: Request, short_code: str):
    url_mapping = await urls_collection.find_one({"short_code": short_code})
    if not url_mapping:
        raise HTTPException(status_code=404, detail="URL not found")
        
    if url_mapping.get("password"):
        return templates.TemplateResponse("password_prompt.html", {
            "request": request,
            "short_code": short_code
        })
    
    return RedirectResponse(url=url_mapping["long_url"])