import csv
import io
import json
import urllib.request
from datetime import datetime

SOURCE_URL = "https://www.jtis.cz/data/courses-history/WDFCA.csv"
OUTPUT_FILE = "CZ1005100543.json"


def download_csv():
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8-sig")


def convert_prices(csv_text):
    reader = csv.reader(io.StringIO(csv_text), delimiter=";")
    rows = list(reader)

    print("CSV rows downloaded:", len(rows))

    prices = []

    for row in rows:
        if len(row) < 2:
            continue

        date_text = row[0].strip()
        price_text = row[1].strip().replace(" ", "").replace(",", ".")

        try:
            date = datetime.strptime(date_text, "%d.%m.%Y")
            price = float(price_text)
        except (ValueError, TypeError):
            continue

        prices.append({
            "date": date.strftime("%Y-%m-%d"),
            "close": price
        })

    prices.sort(key=lambda item: item["date"])

    if not prices:
        raise RuntimeError("No valid prices found in J&T CSV.")

    return prices


def main():
    csv_text = download_csv()
    prices = convert_prices(csv_text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prices, file, ensure_ascii=False, indent=2)

    print("Prices written:", len(prices))
    print("Latest:", prices[-1])


if __name__ == "__main__":
    main()
