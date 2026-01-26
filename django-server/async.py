from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp

sb = sb_cdp.Chrome()
endpoint_url = sb.get_endpoint_url()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.pages[0]
    try:
        page.goto("https://www.harveynorman.com.au/games-hub/game-consoles/playstation-consoles", wait_until="domcontentloaded", timeout=10000)
        page.screenshot(path="screenshot.jpg", full_page=True)
    except Exception as e:
        print(e)