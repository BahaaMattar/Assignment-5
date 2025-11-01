"""
scraper.py
-----------
Scrapes eBay Global Tech Deals using Selenium,
extracts product info, and saves results to ebay_tech_deals.csv.
Compatible with both local and GitHub Actions environments.
"""

import csv
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed
from webdriver_manager.chrome import ChromeDriverManager

URL = "https://www.ebay.com/globaldeals/tech"
CSV_FILE = "ebay_tech_deals.csv"


def fetch_driver():
    """Create and return a configured headless Chrome driver (Linux/Windows compatible)."""
    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--disable-software-rasterizer")
    chrome_opts.add_argument("--remote-debugging-port=9222")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_argument("--disable-extensions")
    chrome_opts.add_argument("--start-maximized")

    # ✅ Automatically install and use the correct ChromeDriver version
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_opts)


def scroll_to_bottom(driver, pause=2):
    """Scrolls down until all lazy-loaded items appear."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def extract_products(driver):
    """Extract all product listings from the main page."""
    cards = driver.find_elements(By.CSS_SELECTOR, "div.dne-itemtile")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_data = []

    for card in cards:
        def safe_find(selector, attr=None):
            try:
                elem = card.find_element(By.CSS_SELECTOR, selector)
                return elem.get_attribute(attr) if attr else elem.text.strip()
            except:
                return "N/A"

        all_data.append({
            "timestamp": now,
            "title": safe_find(".dne-itemtile-title span"),
            "price": safe_find(".dne-itemtile-price"),
            "original_price": safe_find(".itemtile-price-strikethrough"),
            "item_url": safe_find(".dne-itemtile-detail a", "href")
        })
    return all_data


def get_shipping(link):
    """Scrape shipping info from an item page."""
    if not link or link == "N/A" or not link.startswith("http"):
        return "Shipping info unavailable"

    try:
        d = fetch_driver()
        d.get(link)
        time.sleep(2)

        try:
            shipping_elem = d.find_element(
                By.XPATH,
                "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'shipping')]"
            )
            txt = shipping_elem.text.strip()
        except:
            txt = "Shipping info unavailable"

        if not txt or txt.lower() in ["see details", "for shipping", ""]:
            txt = "Shipping info unavailable"

        d.quit()
        return txt
    except Exception:
        try:
            d.quit()
        except:
            pass
        return "Shipping info unavailable"


def save_to_csv(data):
    """Save or append to CSV file."""
    header = ["timestamp", "title", "price", "original_price", "shipping", "item_url"]
    exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not exists:
            writer.writeheader()
        writer.writerows(data)


def main():
    print("🚀 Starting eBay Tech Deals scraper...")
    driver = fetch_driver()
    driver.get(URL)
    time.sleep(5)
    scroll_to_bottom(driver)
    products = extract_products(driver)
    driver.quit()

    print(f"🔍 Found {len(products)} products. Fetching shipping info...")
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(get_shipping, p["item_url"]): p for p in products}
        for fut in as_completed(futures):
            prod = futures[fut]
            prod["shipping"] = fut.result() or "Shipping info unavailable"

    save_to_csv(products)
    print(f"✅ Scraped {len(products)} products successfully. Data saved to {CSV_FILE}.")


if __name__ == "__main__":
    main()
