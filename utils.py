import requests

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
