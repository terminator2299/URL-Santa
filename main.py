from fastapi import FastAPI, Query, Request, Form, HTTPException, Response, Depends, status, Cookie
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import validators
import os
import secrets
from typing import Dict, Optional
from pydantic import BaseModel
from passlib.context import CryptContext
import uuid
from config import users_collection, urls_collection, sessions_collection, client
from datetime import datetime

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Optional: Serve static files if needed in the future
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Helper functions for authentication
async def get_current_user(session_id: str = Cookie(default=None)):
    if session_id:
        try:
            # Find session in MongoDB
            session_doc = await sessions_collection.find_one({"session_id": session_id})
            if session_doc:
                username = session_doc.get("username")
                # Find user in MongoDB
                user_doc = await users_collection.find_one({"username": username})
                if user_doc:
                    return {"username": user_doc["username"], "hashed_password": user_doc["hashed_password"]}
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return None
    return None

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_session(username: str) -> str:
    session_id = str(uuid.uuid4())
    try:
        # Store session in MongoDB
        await sessions_collection.insert_one({
            "session_id": session_id,
            "username": username
        })
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        # Fallback to in-memory storage if MongoDB fails
        if not hasattr(app.state, 'fallback_sessions'):
            app.state.fallback_sessions = {}
        app.state.fallback_sessions[session_id] = username
    return session_id

class URLData(BaseModel):
    url: str
    password: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, user: dict = Depends(get_current_user)):
    if not user:
        # If user is not logged in, redirect to login page
        return RedirectResponse("/login", status_code=302)
    else:
        # If user is logged in, show the main website
        with open("templates/index.html", "r") as f:
            return HTMLResponse(content=f.read())

@app.get("/check")
def check_url(url: str = Query(...)):
    is_valid = validators.url(url)
    return JSONResponse(content={"valid": is_valid})

@app.post("/shorten")
async def shorten_url(request: Request, data: URLData, user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=302)
    
    if not validators.url(data.url):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid URL provided"}
        )
    
    # Generate a short code
    short_code = secrets.token_urlsafe(6)
    
    # Store the mapping with password if provided in MongoDB
    url_doc = {
        "short_code": short_code,
        "url": data.url,
        "password": data.password,
        "username": user["username"],  # Associate URL with user
        "created_at": datetime.utcnow()
    }
    await urls_collection.insert_one(url_doc)
    
    # Get the base URL from the request
    base_url = str(request.base_url).rstrip('/')
    
    # Return the shortened URL
    shortened_url = f"{base_url}/{short_code}"
    return JSONResponse(content={"shortenedUrl": shortened_url})

# Registration endpoint
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/register/", response_class=HTMLResponse)
def register_form_redirect(request: Request):
    return RedirectResponse("/register", status_code=301)

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not username or not password:
        return HTMLResponse("Missing username or password", status_code=400)
    
    try:
        # Check if user exists in MongoDB
        existing_user = await users_collection.find_one({"username": username})
        if existing_user:
            return HTMLResponse("Username already exists", status_code=400)
        
        hashed_password = pwd_context.hash(password)
        # Store user in MongoDB
        await users_collection.insert_one({
            "username": username,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        })
        return RedirectResponse("/login", status_code=302)
    except Exception as e:
        print(f"MongoDB connection error during registration: {e}")
        return HTMLResponse("Database connection error. Please try again.", status_code=500)

# Login endpoint
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login/", response_class=HTMLResponse)
def login_form_redirect(request: Request):
    return RedirectResponse("/login", status_code=301)

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, response: Response):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    
    try:
        # Find user in MongoDB
        user_doc = await users_collection.find_one({"username": username})
        if not user_doc or not pwd_context.verify(password, user_doc["hashed_password"]):
            # Render login page with error message
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Invalid username or password."}
            )
        
        session_id = await create_session(username)
        resp = RedirectResponse("/", status_code=302)
        resp.set_cookie(key="session_id", value=session_id, httponly=True)
        return resp
    except Exception as e:
        print(f"MongoDB connection error during login: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Database connection error. Please try again."}
        )

# Logout endpoint
@app.get("/logout")
async def logout(session_id: str = Cookie(default=None)):
    if session_id:
        # Remove session from MongoDB
        await sessions_collection.delete_one({"session_id": session_id})
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session_id")
    return resp

# Protected dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(user: dict = Depends(get_current_user)):
    if not user:
        return RedirectResponse("/login", status_code=302)
    return f"""
    <html><body>
    <h2>Welcome, {user['username']}!</h2>
    <a href='/logout'>Logout</a>
    </body></html>
    """

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    # Find URL in MongoDB
    url_doc = await urls_collection.find_one({"short_code": short_code})
    if not url_doc:
        return JSONResponse(
            status_code=404,
            content={"error": "Short URL not found"}
        )
    
    url_data = {"url": url_doc["url"], "password": url_doc.get("password")}
    
    # If no password is set, redirect directly
    if not url_data.get("password"):
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; url={url_data['url']}" />
                </head>
                <body>
                    <p>Redirecting to <a href="{url_data['url']}">{url_data['url']}</a>...</p>
                </body>
            </html>
            """
        )
    
    # If password is set, show password form
    return HTMLResponse(
        content=f"""
        <html>
            <head>
                <title>Password Protected URL</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f5f5f5;
                    }}
                    .password-form {{
                        background: white;
                        padding: 2rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    input[type="password"] {{
                        padding: 8px;
                        margin: 10px 0;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                        width: 200px;
                    }}
                    button {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    }}
                    button:hover {{
                        background-color: #45a049;
                    }}
                    .error {{
                        color: red;
                        margin-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="password-form">
                    <h2>Password Protected URL</h2>
                    <p>This URL is password protected. Please enter the password to continue.</p>
                    <form id="passwordForm" onsubmit="return checkPassword(event)">
                        <input type="password" id="password" placeholder="Enter password" required>
                        <br>
                        <button type="submit">Submit</button>
                    </form>
                    <p id="error" class="error" style="display: none;"></p>
                </div>
                <script>
                    async function checkPassword(event) {{
                        event.preventDefault();
                        const password = document.getElementById('password').value;
                        const response = await fetch('/verify-password/{short_code}', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json',
                            }},
                            body: JSON.stringify({{ password: password }}),
                        }});
                        
                        if (response.ok) {{
                            const data = await response.json();
                            window.location.href = data.redirectUrl;
                        }} else {{
                            const error = document.getElementById('error');
                            error.textContent = 'Incorrect password';
                            error.style.display = 'block';
                        }}
                        return false;
                    }}
                </script>
            </body>
        </html>
        """
    )

@app.post("/verify-password/{short_code}")
async def verify_password(short_code: str, data: dict):
    # Find URL in MongoDB
    url_doc = await urls_collection.find_one({"short_code": short_code})
    if not url_doc:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    if data.get("password") == url_doc.get("password"):
        return JSONResponse(content={"redirectUrl": url_doc["url"]})
    
    raise HTTPException(status_code=401, detail="Incorrect password")

@app.get("/test-db")
async def test_db_connection():
    try:
        # Check if we can connect to the database
        await client.admin.command('ping')
        return {"status": "success", "message": "MongoDB connection successful"}
    except Exception as e:
        return {"status": "error", "message": str(e), "type": type(e).__name__}

@app.get("/test-env")
async def test_environment():
    mongodb_url = os.getenv("MONGODB_URL", "NOT_SET")
    return {
        "mongodb_url_set": mongodb_url != "NOT_SET",
        "mongodb_url_preview": mongodb_url[:20] + "..." if len(mongodb_url) > 20 else mongodb_url
    }