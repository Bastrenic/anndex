#import requests
import re
#import difflib
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
from seleniumbase import sb_cdp
from fuzzywuzzy import process, fuzz
#from sentence_transformers import SentenceTransformer, util
import sys

"""

def test():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    sentences = [
        "PS5 PlayStation 5 Pro Console",
        "PS5 PlayStation 5 Slim Console",
        "PS5 PlayStation 5 Slim Digital Console (825GB)",
        "PS5 PlayStation Vertical Stand for PS5 and PS5 Pro",
        "PS5 PlayStation 5 DualSense Wireless Controller Midnight Black",
        'Sony - INZONE H5 Wireless Gaming Headset (For PC/PS5) - Black',
        'Sony - INZONE H9 Wireless Noise Cancelling Gaming Headset (For PC/PS5) - White',
        'Sony - INZONE H9II Wireless Noise Cancelling Headset (For PC/PS5) - Black',
        'Sony - INZONE H9II Wireless Noise Cancelling Headset (For PC/PS5) - White',
        'Sony - INZONE H3 Wired Headset (For PC/PS5) - Black',
        'Disc Drive For PS5 Digital Edition or Pro Console', 
        'PlayStation Portal Remote Player For PS5 Console', 
        'PS5 Cooling Fans, Playstation 5 Cooling Fan Compatible with PS5 Discs Edition and Digital Edition', 
        'PlayStation 5 Disc Console',
        'PlayStation 5 Pro Console',        
        'PlayStation 5 Console Slim', 
        'PlayStation 5 Console Slim Digital Edition',
        'PlayStation 5 Console Fortnite Flowering Chaos Bundle', 
        'PlayStation 5 Console Digital Fortnite Flowering Chaos Bundle', 
        'PlayStation 5 Portal Remote Player',
        'PS5 PlayStation 5 Pro Console',
        'PlayStation VR2',
        'PlayStation 5 Console – 1TB',
        'PlayStation 5 Digital Edition Console – 825GB',
        'Playstation Portal Remote Player',
        'PlayStation 5 Pro Console', 
        'PlayStation 5 Console (Slim)', 
        'PlayStation 5 Digital Edition Console (Slim)', 
        'PlayStation 5 Digital Edition and DualSense controller bundle', 
        'PlayStation 5 Digital Edition Console (Slim) - Fortnite Cobalt Star Bundle',
    ]

    sentence_embeddings = model.encode(sentences)
    query_embeddings = model.encode("ps5")
    results = util.semantic_search(query_embeddings, sentence_embeddings, top_k=1)
    print(results)
"""

item_regex = re.compile(r'(card|tile|product)', re.I)
title_regex = re.compile(r'(title|name)', re.I)
price_regex = re.compile(r'price', re.I)




def scrape_page(query, html_content, link):
    possible_item_tags = [
        {"data-testid": re.compile(r"card", re.I)},
        {"data-testid": re.compile(r"tile", re.I)},
        {"class": re.compile(r"card", re.I)},
        {"class": re.compile(r"tile", re.I)},
        {"class": re.compile(r"(?=.*product)(?=.*summary)", re.I)},
        {"class": re.compile(r"(?=.*product)", re.I)}
        #{"class": re.compile(r"product-info-main", re.I)}
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
        {"data-testid": re.compile(r"price", re.I)},
        {"class": re.compile(r"price", re.I)}
    ]


    matches = []
    items = []
    titles = {}
    soup = BeautifulSoup(html_content, 'lxml')
    name = soup.find("title")
    if name:
        name = name.text

    
    for item_attr in possible_item_tags:
       results = soup.find_all(["div", "li"], attrs=item_attr)
       items.extend(results)
    

    #items = soup.select("div, li")
    #print(len(items))
    #sys.exit()

    for i in items:
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



    with open("matches_test.txt", "a") as f:
        f.write(f"{name}\n")
        f.write(f"{link}\n\n")
        for m in matches:
            title, score = m[0], m[1]
            f.write(f"{title, titles[title], score}\n")
        f.write('\n')
    

def scrape_search(query):
    sb = sb_cdp.Chrome(locale="en")
    endpoint_url = sb.get_endpoint_url()
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint_url)
        context = browser.contexts[0]
        page = context.pages[0]
        try:
            page.goto("https://www.amazon.com.au/BEAUTY-OF-JOSEON-Dynasty-Cream/dp/B08WJQ3XJD?th=1", wait_until="domcontentloaded", timeout=5000)      
            page.wait_for_function("""
                () => document.body.innerText.length > 1000
            """, timeout=5000)
            #page.wait_for_timeout(600)
            html_content = page.content()
            with open('test.html', 'w') as f:
                f.write(html_content)
            #page.screenshot(path="screenshot.jpg", full_page=True)
            #print(html_content)
            #scrape_page(query, html_content, "dynasty cream")
        except TimeoutError:
            print("oops")
            sys.exit()
    

        #soup = BeautifulSoup(html_content, 'lxml')




def main():
    #requests.get('https://www.beautyamora.com.au/dynasty-cream-tube-100ml81841.html')
    
    scrape_search("dynasty cream 100ml")

    #with open('test.html', 'r') as f:
    #    html_content = f.read()

    #scrape_page('test', html_content, 'hello')

if __name__ == "__main__":
    main()
    