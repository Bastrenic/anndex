import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

sb = sb_cdp.Chrome(locale="en")
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.pages[0]
    page.goto("https://www.google.com/search?q=ps5")
    page.screenshot(path="screenshot.jpg", full_page=True)
    content = page.content()

    with open("content.html", "w") as f:
        f.write(content)

    browser.close()



# https://html.duckduckgo.com/html/?q=ps5
"""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}
response = requests.get("https://httpbin.org/user-agent", headers=headers)

with open("content.html", "w") as f:
    f.write(response.text)
"""