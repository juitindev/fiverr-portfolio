"""
scraper.py
===========
Portfolio Example — "Scrape Any Website & Deliver Clean Structured Data"
By: juitindev @ GitHub | Fiverr

Scenario:
    Client wants to monitor product prices from an e-commerce site.
    - Scrapes product name, price, rating, availability
    - Detects price changes between runs
    - Saves results to CSV
    - Sends alert if price drops

Note: Uses books.toscrape.com (a legal scraping sandbox site)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime

BASE_URL   = "https://books.toscrape.com/catalogue/"
START_URL  = "https://books.toscrape.com/catalogue/page-1.html"
OUTPUT_CSV = "products.csv"
HISTORY_CSV= "price_history.csv"
MAX_PAGES  = 5  # scrape first 5 pages

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; portfolio-scraper/1.0)"
}

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def parse_products(soup: BeautifulSoup) -> list[dict]:
    products = []
    for article in soup.select("article.product_pod"):
        name      = article.h3.a["title"]
        price     = float(article.select_one(".price_color").text.replace("£","").replace("Â","").strip())
        rating    = RATING_MAP.get(article.select_one("p.star-rating")["class"][1], 0)
        available = "In stock" in article.select_one(".availability").text
        link      = BASE_URL + article.h3.a["href"].replace("../","")
        products.append({
            "name": name, "price": price,
            "rating": rating, "available": available,
            "url": link, "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return products


def get_next_page(soup: BeautifulSoup) -> str | None:
    btn = soup.select_one("li.next a")
    if btn:
        return BASE_URL + btn["href"]
    return None


def detect_price_changes(new_df: pd.DataFrame) -> pd.DataFrame:
    if not os.path.exists(HISTORY_CSV):
        return pd.DataFrame()
    old_df = pd.read_csv(HISTORY_CSV)
    old_df = old_df.sort_values("scraped_at").groupby("name").last().reset_index()
    merged = new_df.merge(old_df[["name","price"]], on="name", suffixes=("_new","_old"))
    changes = merged[merged["price_new"] != merged["price_old"]].copy()
    changes["change"] = changes["price_new"] - changes["price_old"]
    changes["change_pct"] = (changes["change"] / changes["price_old"] * 100).round(2)
    return changes[["name","price_old","price_new","change","change_pct"]]


def run():
    all_products = []
    url = START_URL
    page = 1

    print(f"🔍 Starting scrape — max {MAX_PAGES} pages\n")

    while url and page <= MAX_PAGES:
        print(f"  Page {page}: {url}")
        soup = get_soup(url)
        products = parse_products(soup)
        all_products.extend(products)
        url = get_next_page(soup)
        page += 1
        time.sleep(0.5)  # polite delay

    df = pd.DataFrame(all_products)
    print(f"\n✅ Scraped {len(df)} products")

    # Detect price changes
    changes = detect_price_changes(df)
    if not changes.empty:
        print(f"\n⚠️  Price changes detected ({len(changes)}):")
        print(changes.to_string(index=False))
    else:
        print("\n📊 No price changes detected since last run.")

    # Save
    df.to_csv(OUTPUT_CSV, index=False)
    df.to_csv(HISTORY_CSV, mode="a", header=not os.path.exists(HISTORY_CSV), index=False)
    print(f"\n💾 Saved → {OUTPUT_CSV}")

    # Summary
    print(f"\n{'='*45}")
    print(f"  Total products : {len(df)}")
    print(f"  Avg price      : £{df['price'].mean():.2f}")
    print(f"  Cheapest       : £{df['price'].min():.2f} — {df.loc[df['price'].idxmin(),'name'][:40]}")
    print(f"  Most expensive : £{df['price'].max():.2f} — {df.loc[df['price'].idxmax(),'name'][:40]}")
    print(f"  In stock       : {df['available'].sum()} / {len(df)}")
    print(f"{'='*45}")


if __name__ == "__main__":
    run()
