import requests
import re
import difflib
import sys
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
from sentence_transformers import SentenceTransformer
from seleniumbase import sb_cdp
from fuzzywuzzy import process

# when parsing amazon - correct price will look like this - ('This item:', '$36.99$36.99')
# make it faster
# write function for parsing title and parsing price
# get the image


def group_results():
    pass
    


def scrape_page(query, html_content, link):
    possible_item_tags = [
        {"data-testid": re.compile(r"card", re.I)},
        {"data-testid": re.compile(r"tile", re.I)},
        {"class": re.compile(r"card", re.I)},
        {"class": re.compile(r"tile", re.I)},
        {"class": re.compile(r"(?=.*product)(?=.*summary)", re.I)},
    ]
    possible_title_tags = [
        {"data-testid": re.compile(r"(?=.*product)(?=.*title)", re.I)},
        {"data-testid": re.compile(r"(?=.*product)(?=.*name)", re.I)},
        {"data-testid": re.compile(r"title", re.I)},
        {"data-testid": re.compile(r"name", re.I)},
        {"class": re.compile(r"(?=.*product)(?=.*title)", re.I)},
        {"class": re.compile(r"(?=.*product)(?=.*name)", re.I)},
        {"class": re.compile(r"title", re.I)},
        {"class": re.compile(r"name", re.I)},
    ]

    possible_price_tags = [
        {"data-testid": re.compile(r"(?=.*product)(?=.*price)", re.I)},
        {"data-testid": re.compile(r"(?=.*ticket)(?=.*price)", re.I)},
        {"data-testid": re.compile(r"price", re.I)},
        {"class": re.compile(r"(?=.*ticket)(?=.*price)", re.I)},
        {"class": re.compile(r"(?=.*product)(?=.*price)", re.I)},
        {"class": re.compile(r"price", re.I)},
    ]


    matches = []
    soup = BeautifulSoup(html_content, 'lxml')
    name = soup.find("title")
    if name:
        name = name.text

    for item_attr in possible_item_tags:
        items = soup.find_all(["div", "li"], attrs=item_attr, recursive=False)


    titles = {}
   
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

    matches = process.extract(query, list(titles.keys()), limit=1)

    if not titles:
        return

    with open("matches.txt", "a") as f:
        f.write(f"{name}\n")
        f.write(f"{link}\n\n")
        for m in matches:
            title = m[0]
            f.write(f"{title, titles[title]}\n")
        f.write('\n')


def scrape_search(query):
    sb = sb_cdp.Chrome(locale="en")
    endpoint_url = sb.get_endpoint_url()
    domains = set()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = context.pages[0]
        page.goto(f"https://html.duckduckgo.com/html/?q={query}", wait_until="domcontentloaded")
        html_content = page.content()

        soup = BeautifulSoup(html_content, 'lxml')
    
        links = soup.find_all('a', attrs={'class', 'result__url'})

        for l in links:            
            l = "https://" + l.text.strip()
            print(l)
            m = re.match(r'https:\/\/([a-zA-Z\d\.]+)', l)
            domain = None
            if m:
                domain = m.group(1)
            if domain in domains:
                continue
            domains.add(domain)
            
            try:
                page.goto(l, wait_until="domcontentloaded", timeout=5000)
                page.wait_for_function("""
                    () => document.body.innerText.length > 1000
                """, timeout=5000)
                html_content = page.content()
                scrape_page(query, html_content, l)
            except Exception as e:
                print(f"Error: {e}")
                continue


def main():
    scrape_search("playstation 5 pro")

if __name__ == "__main__":
    main()
    

    #page.wait_for_timeout(500)