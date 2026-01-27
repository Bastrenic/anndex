import requests
import re
import difflib
import sys
import asyncio
import concurrent.futures
from bs4 import BeautifulSoup
from itertools import repeat
from playwright.async_api import async_playwright, TimeoutError
from sentence_transformers import SentenceTransformer
from seleniumbase import cdp_driver
from fuzzywuzzy import process, fuzz

# when parsing amazon - correct price will look like this - ('This item:', '$36.99$36.99') --> consider specialised parsing for ebay and amazon?
# make it faster
# write function for parsing title and parsing price
# get the image
# discard results if score is too low


def group_results():
    pass
    

domains = set()

def scrape_page(query, html_content, link):
    possible_item_tags = [
        {"data-testid": re.compile(r"card", re.I)},
        {"data-testid": re.compile(r"tile", re.I)},
        {"class": re.compile(r"card", re.I)},
        {"class": re.compile(r"tile", re.I)},
        {"class": re.compile(r"(?=.*product)", re.I)},
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
    items = []
    soup = BeautifulSoup(html_content, 'lxml')
    name = soup.find("title")
    if name:
        name = name.text

    for item_attr in possible_item_tags:
        items.extend(soup.find_all(["div", "li"], attrs=item_attr))

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
        
        if len(titles) > 20:
            break

    match = process.extractOne(query, titles.keys(), scorer=fuzz.token_set_ratio)

    if not titles:
        return

    title, score = match

    with open("matches.txt", "a") as f:
        f.write(f"{name}\n")
        f.write(f"{link}\n\n")
        f.write(f"{title, titles[title]}\n")
        f.write('\n')


async def query_page(context, query, link):
    m = re.match(r'https:\/\/([a-zA-Z\d\.]+)', link)
    if m:
        domain = m.group(1)

    if domain in domains:
        return
    domains.add(domain)

    page = await context.new_page()
    try:
        await page.goto(link, wait_until="domcontentloaded", timeout=5000)
        await page.wait_for_function("""
            () => document.body.innerText.length > 1000
        """, timeout=5000)
        html_content = await page.content()
        await asyncio.to_thread(scrape_page, query, html_content, link)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await page.close()




async def main(query):
    driver = await cdp_driver.start_async()
    endpoint_url = driver.get_endpoint_url()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = context.pages[0]
        await page.goto(f"https://html.duckduckgo.com/html/?q={query}", wait_until="domcontentloaded")
        html_content = await page.content()

        soup = BeautifulSoup(html_content, 'lxml')
    
        links = ['https://' + l.text.strip() for l in soup.find_all('a', attrs={'class', 'result__url'})]
        await asyncio.gather(*[query_page(await browser.new_context(), query, link) for link in links])



if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main('ps5'))
    
