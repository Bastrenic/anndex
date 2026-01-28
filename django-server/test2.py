from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError
from seleniumbase import sb_cdp


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
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'lxml')
        img_tags = soup.find_all('img')
        for i in img_tags[:1]:
            src = i.get('src')
            response = requests.get()
    except TimeoutError:
        print("oops")
        sys.exit()