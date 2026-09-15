import json
import re
import urllib.request
from datetime import datetime
from html import unescape

SOURCE_URL = "https://woodis.cz/produkty/fondy/"
OUTPUT_FILE = "CZ0008477551.json"
ISIN = "CZ0008477551"


def download_page():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def get_current_price(html):
    # Převede HTML na text a zachová mezery mezi jednotlivými prvky.
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    # Najdeme přesně náš ISIN.
    position = text.find(ISIN)

    if position == -1:
        raise RuntimeError(f"ISIN {ISIN} nebyl na stránce WOOD nalezen.")

    # Potřebujeme pouze krátký úsek ZA naším ISIN.
    segment = text[position:position + 300]

    # Oficiální tabulka:
    # ISIN | CZK | 11. 9. 2026 | 1,2825
    pattern = (
        rf"{ISIN}\s+CZK\s+"
        r"(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})\s+"
        r"(\d+[,.]\d+)"
    )

    match = re.search(pattern, segment)

    if not match:
        raise RuntimeError(
            "ISIN byl nalezen, ale datum a NAV se nepodařilo bezpečně přečíst."
        )

    date_text = match.group(1)
    price_text = match.group(2)

    date_text = re.sub(r"\s+", "", date_text)
    date = datetime.strptime(date_text, "%d.%m.%Y")
    price = float(price_text.replace(",", "."))

    # Ochrana proti nesmyslné hodnotě.
    if not 0.5 < price < 5:
        raise RuntimeError(f"Podezřelá hodnota NAV: {price}")

    return date.strftime("%Y-%m-%d"), price


def load_history():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise RuntimeError(
            f"{OUTPUT_FILE} neexistuje. Historie nebude vytvořena ani přepsána."
        )

    if not isinstance(data, list) or not data:
        raise RuntimeError("Existující JSON neobsahuje platnou historii.")

    return data


def main():
    html = download_page()
    date, price = get_current_price(html)

    print("WOOD current NAV:", date, price)

    prices = load_history()

    # Zachováme historii a případný stejný den pouze aktualizujeme.
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

    print("Total prices:", len(prices))
    print("Latest:", prices[-1])


if __name__ == "__main__":
    main()import json
import re
import urllib.request
from datetime import datetime
from html import unescape

SOURCE_URL = "https://woodis.cz/produkty/fondy/"
OUTPUT_FILE = "CZ0008477551.json"
ISIN = "CZ0008477551"


def download_page():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def get_current_price(html):
    # Převede HTML na text a zachová mezery mezi jednotlivými prvky.
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text)

    # Najdeme přesně náš ISIN.
    position = text.find(ISIN)

    if position == -1:
        raise RuntimeError(f"ISIN {ISIN} nebyl na stránce WOOD nalezen.")

    # Potřebujeme pouze krátký úsek ZA naším ISIN.
    segment = text[position:position + 300]

    # Oficiální tabulka:
    # ISIN | CZK | 11. 9. 2026 | 1,2825
    pattern = (
        rf"{ISIN}\s+CZK\s+"
        r"(\d{1,2}\.\s*\d{1,2}\.\s*\d{4})\s+"
        r"(\d+[,.]\d+)"
    )

    match = re.search(pattern, segment)

    if not match:
        raise RuntimeError(
            "ISIN byl nalezen, ale datum a NAV se nepodařilo bezpečně přečíst."
        )

    date_text = match.group(1)
    price_text = match.group(2)

    date_text = re.sub(r"\s+", "", date_text)
    date = datetime.strptime(date_text, "%d.%m.%Y")
    price = float(price_text.replace(",", "."))

    # Ochrana proti nesmyslné hodnotě.
    if not 0.5 < price < 5:
        raise RuntimeError(f"Podezřelá hodnota NAV: {price}")

    return date.strftime("%Y-%m-%d"), price


def load_history():
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise RuntimeError(
            f"{OUTPUT_FILE} neexistuje. Historie nebude vytvořena ani přepsána."
        )

    if not isinstance(data, list) or not data:
        raise RuntimeError("Existující JSON neobsahuje platnou historii.")

    return data


def main():
    html = download_page()
    date, price = get_current_price(html)

    print("WOOD current NAV:", date, price)

    prices = load_history()

    # Zachováme historii a případný stejný den pouze aktualizujeme.
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

    print("Total prices:", len(prices))
    print("Latest:", prices[-1])


if __name__ == "__main__":
    main()
