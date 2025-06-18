from fastapi import FastAPI, Query, Request, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import validators
import os
import secrets
from typing import Dict, Optional
from pydantic import BaseModel

app = FastAPI()

# Store shortened URLs with their passwords (in a real application, you'd use a database)
url_mapping: Dict[str, Dict[str, str]] = {}

# Optional: Serve static files if needed in the future
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    if short_code not in url_mapping:
        return JSONResponse(
            status_code=404,
            content={"error": "Short URL not found"}
        )
    
    url_data = url_mapping[short_code]
    
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
    if short_code not in url_mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    url_data = url_mapping[short_code]
    if data.get("password") == url_data.get("password"):
        return JSONResponse(content={"redirectUrl": url_data["url"]})
    
    raise HTTPException(status_code=401, detail="Incorrect password")
