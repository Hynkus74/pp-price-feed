import json
import re
import urllib.request
from datetime import datetime

SOURCE_URL = "https://woodis.cz/produkty/fondy/wood-company-realitni-opf/"
OUTPUT_FILE = "CZ0008477551.json"
ISIN = "CZ0008477551"


def download_page():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html,application/xhtml+xml"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_current_nav(html):
    # Bezpečnostní kontrola: musí jít o správný fond.
    if ISIN not in html:
        raise RuntimeError(f"Na stránce nebyl nalezen ISIN {ISIN}.")

    # HTML převedeme na prostý text.
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)

    # Hledáme výslovně "Datum poslední valuace".
    date_match = re.search(
        r"Datum poslední valuace:\s*(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})",
        text,
        flags=re.I
    )

    if not date_match:
        raise RuntimeError("Nenalezeno 'Datum poslední valuace'.")

    # Hledáme cenu spojenou výslovně s textem
    # "Hodnota investiční akcie".
    price_match = re.search(
        r"(\d+[,.]\d+)\s*CZK\s*Hodnota investiční akcie",
        text,
        flags=re.I
    )

    if not price_match:
        raise RuntimeError("Nenalezena 'Hodnota investiční akcie'.")

    date_text = re.sub(r"\s+", "", date_match.group(1))
    date = datetime.strptime(date_text, "%d.%m.%Y")

    price = float(price_match.group(1).replace(",", "."))

    if not 0.5 < price < 5:
        raise RuntimeError(f"Podezřelá hodnota NAV: {price}")

    return date.strftime("%Y-%m-%d"), price


def load_history():
    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        prices = json.load(file)

    if not isinstance(prices, list) or not prices:
        raise RuntimeError("Historický JSON je prázdný nebo neplatný.")

    return prices


def main():
    html = download_page()
    date, price = extract_current_nav(html)

    print("WOOD NAV nalezen:")
    print("Date:", date)
    print("Price:", price)

    prices = load_history()

    # Pokud datum už existuje, nahradíme pouze jeho cenu.
    prices = [
        item for item in prices
        if item.get("date") != date
    ]

    prices.append({
        "date": date,
        "close": price
    })

    prices.sort(key=lambda item: item["date"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prices, file, ensure_ascii=False, indent=2)

    print("Celkem zaznamu:", len(prices))
    print("Posledni zaznam:", prices[-1])


if __name__ == "__main__":
    main()
