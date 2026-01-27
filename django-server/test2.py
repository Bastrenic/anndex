import re
from bs4 import BeautifulSoup
from rapidfuzz import process, fuzz   # faster than fuzzywuzzy

# -------- precompiled regex (CRITICAL for speed) --------
ITEM_RE  = re.compile(r"(card|tile|product)", re.I)
TITLE_RE = re.compile(r"(title|name)", re.I)
PRICE_RE = re.compile(r"price", re.I)


def attr_matches(tag, regex):
    """Check all attributes of a tag for a regex match."""
    for v in tag.attrs.values():
        if isinstance(v, str) and regex.search(v):
            return True
        if isinstance(v, list):
            for x in v:
                if regex.search(x):
                    return True
    return False


def scrape_page(query, html_content, link):
    soup = BeautifulSoup(html_content, "lxml")

    page_title = soup.title.text if soup.title else ""

    titles = {}
    query_tokens = set(query.lower().split())

    # -------- ONE DOM SCAN ONLY --------
    for container in soup.select("div, li"):

        if not attr_matches(container, ITEM_RE):
            continue

        title = None
        price = None

        # -------- SINGLE PASS THROUGH CHILDREN --------
        for el in container.descendants:
            if not hasattr(el, "attrs"):
                continue

            if title is None and attr_matches(el, TITLE_RE):
                title = el.get_text(strip=True)

            elif price is None and attr_matches(el, PRICE_RE):
                price = el.get_text(strip=True)

            if title and price:
                break

        if not title or not price:
            continue

        # -------- TOKEN FILTER (huge speed win) --------
        title_l = title.lower()
        if not any(tok in title_l for tok in query_tokens):
            continue

        titles[title] = price

        # early exit: we don’t need hundreds of items
        if len(titles) >= 25:
            break

    print(len(titles))
    if not titles:
        return

    # -------- FAST FUZZY MATCH --------
    match = process.extractOne(
        query,
        titles.keys(),
        scorer=fuzz.token_set_ratio
    )

    if not match:
        return

    best_title, score = match

    # -------- OUTPUT --------
    with open("matches2.txt", "a", encoding="utf-8") as f:
        f.write(f"{page_title}\n")
        f.write(f"{link}\n\n")
        f.write(f"{best_title} — {titles[best_title]} (score={score})\n")
        f.write("\n")

def main():
    with open('test.html', 'r') as f:
        html_content = f.read()
    scrape_page('test', html_content, 'test')

if __name__ == "__main__":
    main()
