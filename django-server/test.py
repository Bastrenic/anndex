import requests
import re
import difflib
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp
from fuzzywuzzy import process
import sys


"""
MAIN STUFF

sb = sb_cdp.Chrome(locale="en")
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.pages[0]
    page.goto("https://www.costco.com.au/Computers/Gaming/Gaming-Consoles/PS5-PlayStation-5-Slim-Console/p/181737")
    page.wait_for_timeout(500)
    page.screenshot(path="screenshot2.jpg", full_page=True)
    html_content = page.content()

with open("content7.html" ,"w") as f:
    f.write(html_content)
"""


"""
JB HI FI
html_page = "content1.html"
item_attrs = {"class": re.compile(r"card", re.I)}
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

BIG W

html_page = "content4.html"
item_attrs = {"class": re.compile(r"tile", re.I)}
title_attrs = {"class": re.compile(r"name", re.I)}
price_attrs = {"class": re.compile(r"price", re.I)}


THE GOOD GUYS

html_page = "content5.html"
item_attrs = {"data-testid": re.compile(r"card", re.I)}
title_attrs = {"class": re.compile(r"title", re.I)}
price_attrs = {"class": re.compile(r"price", re.I)}


COSTCO

html_page = "content7.html"
item_attrs = {"data-testid": re.compile(r"card", re.I)}
title_attrs = {"class": re.compile(r"product-name", re.I)}
price_attrs = {"class": re.compile(r"product-price", re.I)}
"""

# write a function to parse product name and product price
# product name - cut as soon as '\n' is reached?
# product price - start at the first number, and keep going until the next character is no longer a decimal or number or the string has ended

html_page = "content7.html"
name = "COSTCO"
possible_item_tags = [
    {"data-testid": re.compile(r"card", re.I)},
    {"data-testid": re.compile(r"tile", re.I)},
    {"class": re.compile(r"card", re.I)},
    {"class": re.compile(r"tile", re.I)}
]
possible_title_tags = [
    {"data-testid": re.compile(r"(?=.*product)(?=.*title)", re.I)},
    {"data-testid": re.compile(r"(?=.*product)(?=.*name)", re.I)},
    {"data-testid": re.compile(r"title", re.I)},
    {"data-testid": re.compile(r"name", re.I)},
    {"class": re.compile(r"(?=.*product)(?=.*title)", re.I)},
    {"class": re.compile(r"(?=.*product)(?=.*name)", re.I)},
    {"class": re.compile(r"title", re.I)},
    {"class": re.compile(r"name", re.I)}
]

possible_price_tags = [
    {"data-testid": re.compile(r"(?=.*product)(?=.*price)", re.I)},
    {"data-testid": re.compile(r"(?=.*ticket)(?=.*price)", re.I)},
    {"data-testid": re.compile(r"price", re.I)},
    {"class": re.compile(r"(?=.*ticket)(?=.*price)", re.I)},
    {"class": re.compile(r"(?=.*product)(?=.*price)", re.I)},
    {"class": re.compile(r"price", re.I)}
]


query = "ps5"
matches = []
with open(html_page, "r") as f:
    html_content = f.read()
soup = BeautifulSoup(html_content, 'html.parser')

for item_attr in possible_item_tags:
    items = soup.find_all(["div", "li"], attrs=item_attr)
    if items:
        break

titles = {}
if not items:
    # on single item page
    for title_attr in possible_title_tags:
        title = soup.find(attrs=title_attr)
        if title:
            sys.exit()
            break
    
    for price_attr in possible_price_tags:
        price = soup.find(attrs=price_attr)
        if price: 
            break

    if title and price:
        title = title.text.strip()
        price = price.text.strip()

        titles[title] = price
    matches.append((title, price))

else:
    for i in items:
        # how to skip duplicates?
        for title_attr in possible_title_tags:
            title = i.find(attrs=title_attr)
            if title:
                break
        
        for price_attr in possible_price_tags:
            price = i.find(attrs=price_attr)
            if price: 
                break

        if title and price:
            title_children = title.find_all(recursive=False)
            if title_children:
                title = title_children[0]
            titles[title.text.strip()] = price.text.strip()

    matches = process.extract(query, list(titles.keys()), limit=10)


with open("matches.txt", "a") as f:
    f.write(f"{name}\n\n")
    for m in matches:
        title = m[0]
        f.write(f"{title, titles[title]}\n")
    f.write('\n')
