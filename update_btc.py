import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta

START_YEAR = 2024
OUTPUT_FILE = "BTC-CZK.json"

BTC_URL = (
    "https://raw.githubusercontent.com/"
    "viratsoft/btc-price-json/main/json/{year}.json"
)

ECB_URL = (
    "https://www.ecb.europa.eu/stats/eurofxref/"
    "eurofxref-hist.xml"
)


def download_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download_ecb_rates():
    req = urllib.request.Request(
        ECB_URL,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    rates = {}

    # ECB XML uses namespaces, so we inspect elements by their attributes.
    for elem in root.iter():
        day = elem.attrib.get("time")

        if not day:
            continue

        usd = None
        czk = None

        for child in elem:
            currency = child.attrib.get("currency")
            rate = child.attrib.get("rate")

            if currency == "USD":
                usd = float(rate)
            elif currency == "CZK":
                czk = float(rate)

        if usd is not None and czk is not None:
            # ECB rates are units of currency per 1 EUR.
            # CZK per USD = CZK/EUR divided by USD/EUR.
            rates[day] = czk / usd

    return rates


def previous_available_fx(day, fx_rates):
    d = date.fromisoformat(day)

    # BTC trades every day, ECB publishes rates only on business days.
    # For weekends/holidays use the most recent preceding ECB rate.
    for _ in range(10):
        key = d.isoformat()

        if key in fx_rates:
            return fx_rates[key]

        d -= timedelta(days=1)

    raise RuntimeError(f"Chybí ECB kurz pro {day}")


def main():
    today = date.today()

    print("Stahuji ECB USD/CZK historii...")
    fx_rates = download_ecb_rates()

    output = []

    for year in range(START_YEAR, today.year + 1):
        print(f"Stahuji BTC/USD {year}...")

        btc_prices = download_json(
            BTC_URL.format(year=year)
        )

        for day, btc_usd in btc_prices.items():
            d = date.fromisoformat(day)

            if d > today:
                continue

            usd_czk = previous_available_fx(day, fx_rates)

            btc_czk = float(btc_usd) * usd_czk

            output.append({
                "date": day,
                "close": round(btc_czk, 2)
            })

    output.sort(key=lambda x: x["date"])

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Hotovo: {OUTPUT_FILE} "
        f"({len(output)} denních kurzů)"
    )


if __name__ == "__main__":
    main()
