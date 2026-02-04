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


def parse_title(title):
    return title.text.strip()

def parse_price(price):
    price = price.text.strip()
    res = ''
    digit_phase = False
    whitelist = set('0123456789.,')

    for p in price:
        if p not in whitelist:
            if not digit_phase:
                continue
            else: 
                break

        if p in whitelist:
            if not digit_phase:
                digit_phase = True
            res += p
    return res

def parse_amazon_page(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    title = parse_title(soup.find('span', attrs={'id': 'productTitle'}))
    price = parse_price(soup.find('span', attrs={'class': re.compile(r'a-price', re.I)}))
    return title, price
    
name_to_parse_function = {'amazon': parse_amazon_page}
img_url = None

def scrape_page(query, html_content, link, domain):
    # check for hard coded popular sites
    if domain and domain in name_to_parse_function:
        return name_to_parse_function[domain](html_content), link

    possible_img_tags = [
        {"alt": re.compile(query, re.I)},
        {"title": re.compile(query, re.I)}
    ]

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
    global img_url

    name = soup.find("title")
    if name:
        name = name.text

    for item_attr in possible_item_tags:
        items.extend(soup.find_all(["div", "li"], attrs=item_attr))

    titles = {}
   
    for i in items:
        # how to skip duplicates?
        if not img_url:
            for img_attr in possible_img_tags:
                img = i.find(attrs=img_attr)
                if img:
                    img_url = img.get('src')
                    break

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
            titles[parse_title(title)] = parse_price(price)
        
        if len(titles) > 20:
            break

    match = process.extractOne(query, titles.keys(), scorer=fuzz.token_set_ratio)

    if not titles:
        return None

    title, score = match
    return {'name': title, 'price': titles[title], 'link': link, 'domain': domain}



async def query_page(context, lock, query, link, domain_list):
    m = re.match(r'https:\/\/(?:www\.)?([a-zA-Z\d.]+?)\/', link)
    domain = None
    if m:
        domain = m.group(1)
        async with lock:
            if domain in domain_list:
                return None
            domain_list.add(domain)

    page = await context.new_page()
    res = None
    try:
        await page.goto(link, wait_until="domcontentloaded")
        await page.wait_for_function("""
            () => document.body && document.body.innerText.length > 1000
        """, timeout=7500)
        html_content = await page.content()
        res = scrape_page(query, html_content, link, domain)
    except Exception as e:
        print(f"Error: {e}: {link}")
    finally:
        await page.close()
    return res

async def search_results(query):
    products = []
    domains = set()

    driver = await cdp_driver.start_async()
    endpoint_url = driver.get_endpoint_url()

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(endpoint_url)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://html.duckduckgo.com/html/?q={query}", wait_until="domcontentloaded")
        html_content = await page.content()
        await page.close()

        soup = BeautifulSoup(html_content, 'lxml')
        lock = asyncio.Lock()
        
        links = ['https://' + l.text.strip() + '/' for l in soup.find_all('a', attrs={'class': 'result__url'})]
        results = await asyncio.gather(*[query_page(context, lock, query, link, domains) for link in links])
        await browser.close()

    return [i for i in results if i], img_url

if __name__ == "__main__":
    asyncio.run(search_results('ps5'))
