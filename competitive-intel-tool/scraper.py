import requests
from bs4 import BeautifulSoup

def fetch_website_content(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.stripped_strings
        content = ' '.join(texts)
        return content[:3000]
    except Exception as e:
        return f"Error fetching {url}: {e}"
