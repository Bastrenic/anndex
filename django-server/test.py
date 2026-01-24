import requests
import re
import difflib
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp
from fuzzywuzzy import process


"""
MAIN STUFF

sb = sb_cdp.Chrome(locale="en")
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.pages[0]
    page.goto("https://www.ebgames.com.au/featured/playstation-5")
    #page.screenshot(path="screenshot2.jpg", full_page=True)
    html_content = page.content()

with open("content3.html" ,"w") as f:
    f.write(html_content)
"""


"""
JB HI FI
html_page = "content1.html"
item_attrs = {"class": re.compile(r"(card|tile)", re.I)}
title_attrs = {"data-testid": re.compile(r"title", re.I)}
price_attrs = {"data-testid": re.compile(r"price", re.I)}


SONY
html_page = "content2.html"
item_attrs = {"class": re.compile(r"tile", re.I)}
title_attrs = {"class": re.compile(r"name", re.I)}
price_attrs = {"class": re.compile(r"price", re.I)}

EB GAMES
html_page = "content3.html"
item_attrs = {"class": re.compile(r"tile", re.I)}
title_attrs = {"class": re.compile(r"name", re.I)}
price_attrs = {"class": re.compile(r"price", re.I)}

"""


html_page = "content3.html"
item_attrs = {"class": re.compile(r"(card|tile)", re.I)}
title_attrs = {"data-testid": re.compile(r"title", re.I)}
price_attrs = {"data-testid": re.compile(r"price", re.I)}

query = "ps5"


with open(html_page, "r") as f:
    html_content = f.read()
soup = BeautifulSoup(html_content, 'html.parser')
items = soup.find_all("div", attrs=item_attrs)

res = set()
for i in items:
    title = i.find(attrs=title_attrs)
    price = i.find(attrs=price_attrs)
    if title and price:
        res.add((title.text.strip(), price.text.strip()))

titles = []
for title, price in res:
    titles.append(title)

matches = process.extract(query, titles)
print(matches)




 












# https://html.duckduckgo.com/html/?q=ps5
"""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
}
response = requests.get("https://httpbin.org/user-agent", headers=headers)

with open("content.html", "w") as f:
    f.write(response.text)
"""

"""
www.jbhifi.com.au/pages/playstation-5
store.sony.com.au/playstation-5-console
www.bigw.com.au/gaming/ps5/ps5-consoles/c/64121178100
www.thegoodguys.com.au/gaming/gaming-hardware/playstation-consoles
www.ebgames.com.au/featured/playstation-5
www.harveynorman.com.au/games-hub/game-consoles/playstation-consoles
www.telstra.com.au/entertainment/gaming/playstation-consoles
www.target.com.au/p/playstation-5-console-digital-edition-slim/69871610
www.costco.com.au/Computers/Gaming/Gaming-Consoles/PS5-PlayStation-5-Slim-Console/p/181737

"""