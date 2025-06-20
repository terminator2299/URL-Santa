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

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store: {username: {"username": ..., "hashed_password": ...}}
users: Dict[str, Dict[str, str]] = {}

# Simple session store: {session_id: username}
sessions: Dict[str, str] = {}

# Store shortened URLs with their passwords (in a real application, you'd use a database)
url_mapping: Dict[str, Dict[str, str]] = {}

# Optional: Serve static files if needed in the future
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class URLData(BaseModel):
    url: str
    password: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/check")
def check_url(url: str = Query(...)):
    is_valid = validators.url(url)
    return JSONResponse(content={"valid": is_valid})

@app.post("/shorten")
async def shorten_url(request: Request, data: URLData):
    if not validators.url(data.url):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid URL provided"}
        )
    
    # Generate a short code
    short_code = secrets.token_urlsafe(6)
    
    # Store the mapping with password if provided
    url_mapping[short_code] = {
        "url": data.url,
        "password": data.password
    }
    
    # Get the base URL from the request
    base_url = str(request.base_url).rstrip('/')
    
    # Return the shortened URL
    shortened_url = f"{base_url}/{short_code}"
    return JSONResponse(content={"shortenedUrl": shortened_url})


    
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



# Helper functions for authentication

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_session(username: str) -> str:
    session_token = secrets.token_urlsafe(16)
    sessions[session_token] = username
    return session_token

def get_current_user(session_id: str = Cookie(default=None)):
    if session_id and session_id in sessions:
        username = sessions[session_id]
        return users.get(username)
    return None

# Registration endpoint
@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    if not username or not password:
        return HTMLResponse("Missing username or password", status_code=400)
    if username in users:
        return HTMLResponse("Username already exists", status_code=400)
    hashed_password = pwd_context.hash(password)
    users[username] = {"username": username, "hashed_password": hashed_password}
    return RedirectResponse("/login", status_code=302)

# Login endpoint
@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, response: Response):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    user = users.get(username)
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        # Render login page with error message
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid username or password."}
        )
    session_id = str(uuid.uuid4())
    sessions[session_id] = username
    resp = RedirectResponse("/", status_code=302)
    resp.set_cookie(key="session_id", value=session_id, httponly=True)
    return resp

# Logout endpoint
@app.get("/logout")
def logout(session_id: str = Cookie(default=None)):
    if session_id and session_id in sessions:
        sessions.pop(session_id)
    resp = RedirectResponse("/login", status_code=302)
    resp.delete_cookie("session_id")
    return resp

# Protected dashboard route
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(user: dict = Depends(get_current_user)):
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
    if short_code not in url_mapping:
        return JSONResponse(
            status_code=404,
            content={"error": "Short URL not found"}
        )
    
    url_data = url_mapping[short_code]

    @app.post("/verify-password/{short_code}")
    async def verify_password(short_code: str, data: dict):
        if short_code not in url_mapping:
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        url_data = url_mapping[short_code]
        if data.get("password") == url_data.get("password"):
            return JSONResponse(content={"redirectUrl": url_data["url"]})
        
        raise HTTPException(status_code=401, detail="Incorrect password")