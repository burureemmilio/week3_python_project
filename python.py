import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

URL = "https://books.toscrape.com/"
BASE_CURRENCY = "GBP"
TARGET_CURRENCY = "KES"

try:
    # Scrape books
    response = requests.get(URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")[:10]

    products = []

    # Get exchange rate
    rate_url = f"https://open.er-api.com/v6/latest/{BASE_CURRENCY}"
    rate_response = requests.get(rate_url, timeout=10)
    rate_response.raise_for_status()

    rate_data = rate_response.json()
    exchange_rate = rate_data["rates"][TARGET_CURRENCY]

    for book in books:
        title = book.h3.a["title"]
        price_text = book.find("p", class_="price_color").text

        # Example: £51.77 -> 51.77
        price = float(re.search(r"\d+\.\d+", price_text).group())

        converted_price = price * exchange_rate

        products.append({
            "Product Name": title,
            f"Price ({BASE_CURRENCY})": price,
            f"Price ({TARGET_CURRENCY})": round(converted_price, 2)
        })

    df = pd.DataFrame(products)

    print(df)

    df.to_csv("converted_book_prices.csv", index=False)
    print("\nData saved to converted_book_prices.csv")

except requests.exceptions.ConnectionError:
    print("Connection error. Please check your internet connection.")

except requests.exceptions.Timeout:
    print("The request timed out. Try again later.")

except requests.exceptions.RequestException as e:
    print("Something went wrong while requesting data:", e)

except KeyError:
    print("Currency not found. Check if the currency code is correct.")