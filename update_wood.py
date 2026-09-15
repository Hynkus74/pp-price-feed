import json
import re
import urllib.parse
import urllib.request
from datetime import date

SOURCE_URL = "https://www.kkip.cz/cs/fondy/historicke-ceny?add=354"
FUND_ID = "354"
OUTPUT_FILE = "CZ0008477551.json"

DATE_FROM = "01.01.2023"


def download_history():
    data = urllib.parse.urlencode({
        "fundId": FUND_ID,
        "dateFrom": DATE_FROM,
        "dateTo": date.today().strftime("%d.%m.%Y"),
        "send": "Zobrazit",
        "_do": "fundPeriodForm-submit",
    }).encode("utf-8")

    request = urllib.request.Request(
        SOURCE_URL,
        data=data,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_prices(html):
    # KKIP v HTML ukládá data grafu jako trojice:
    # [timestamp_v_ms, vykonnost, NAV]
    pattern = re.compile(
        r"\[\s*(\d{13})\s*,\s*-?\d+(?:\.\d+)?\s*,\s*(\d+(?:\.\d+)?)\s*\]"
    )

    prices = {}

    for timestamp_ms, nav_text in pattern.findall(html):
        timestamp = int(timestamp_ms) / 1000
        day = date.fromtimestamp(timestamp).isoformat()
        nav = float(nav_text)

        # ochrana proti zachycení jiných dat grafu
        if 0.5 < nav < 5:
            prices[day] = nav

    result = [
        {"date": day, "close": prices[day]}
        for day in sorted(prices)
    ]

    if not result:
        raise RuntimeError(
            "V odpovedi KKIP nebyly nalezeny zadne ceny fondu."
        )

    return result


def main():
    html = download_history()
    print("HTML length:", len(html))
    print("Contains 1.2818:", "1.2818" in html)

    pos = html.find("1.2818")
    if pos >= 0:
        print("HTML around 1.2818:")
        print(html[max(0, pos - 500):pos + 500])
    else:
        print("First 2000 characters of response:")
        print(html[:2000])
    prices = extract_prices(html)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(prices, file, ensure_ascii=False, indent=2)

    print("Prices written:", len(prices))
    print("First:", prices[0])
    print("Latest:", prices[-1])


if __name__ == "__main__":
    main()
