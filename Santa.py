import requests
from urllib.parse import urlparse


def validate_urls(url_list, uncheckable_domains):
    results = {}
    for url in url_list:
        domain = urlparse(url).netloc
        if domain in uncheckable_domains:
            results[url] = "Uncheckable"
            continue
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            if response.status_code == 200:
                results[url] = "Valid"
            elif 300 <= response.status_code < 400:
                results[url] = "Redirect"
            elif response.status_code == 404:
                results[url] = "Not Found"
            elif 400 <= response.status_code < 500:
                results[url] = "Client Error"
            elif 500 <= response.status_code < 600:
                results[url] = "Server Error"
        except requests.exceptions.RequestException as e:
            results[url] = str(e)
    return results


urls = ["https://www.example.com", "https://www.nonexistentwebsite.com"]
uncheckable_domains = ["www.walmart.com", "www.twitter.com"]
results = validate_urls(urls, uncheckable_domains)

for url, status in results.items():
    print(f"URL: {url}\nStatus: {status}\n")
