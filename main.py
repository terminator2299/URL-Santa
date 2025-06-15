from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import validators
import os
import secrets
from typing import Dict

app = FastAPI()

# Store shortened URLs (in a real application, you'd use a database)
url_mapping: Dict[str, str] = {}

# Optional: Serve static files if needed in the future
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/check")
def check_url(url: str = Query(...)):
    is_valid = validators.url(url)
    return JSONResponse(content={"valid": is_valid})

@app.get("/shorten")
def shorten_url(url: str = Query(...)):
    if not validators.url(url):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid URL provided"}
        )
    
    # Generate a short code
    short_code = secrets.token_urlsafe(6)
    
    # Store the mapping
    url_mapping[short_code] = url
    
    # Return the shortened URL
    shortened_url = f"http://localhost:8000/{short_code}"
    return JSONResponse(content={"shortenedUrl": shortened_url})

@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    if short_code in url_mapping:
        return HTMLResponse(
            content=f"""
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; url={url_mapping[short_code]}" />
                </head>
                <body>
                    <p>Redirecting to <a href="{url_mapping[short_code]}">{url_mapping[short_code]}</a>...</p>
                </body>
            </html>
            """
        )
    return JSONResponse(
        status_code=404,
        content={"error": "Short URL not found"}
    )
