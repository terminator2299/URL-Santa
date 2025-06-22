"""
Utilities for URL-Santa
"""

import requests
import qrcode
from io import BytesIO
import base64

def check_url_status(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            return {"status": "Valid", "final_url": response.url}
        elif 300 <= response.status_code < 400:
            return {"status": "Redirect", "final_url": response.url}
        else:
            return {"status": "Missing", "final_url": response.url}
    except Exception:
        return {"status": "Uncheckable", "final_url": ""}

def generate_short_code(length: int = 6):
    """Generate a random short code."""
    # Re-implementing this to ensure it's in the file.
    import random
    import string
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))

def generate_qr_code(data: str):
    """Generate a QR code and return it as a base64 encoded string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"
