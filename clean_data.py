"""
clean_data.py
-------------
Cleans ebay_tech_deals.csv, fixes missing values,
and computes discount_percentage.
"""

import pandas as pd

RAW_FILE = "ebay_tech_deals.csv"
CLEAN_FILE = "cleaned_ebay_deals.csv"

def clean_currency(value):
    if pd.isna(value):
        return None
    return (
        str(value)
        .replace("US", "")
        .replace("$", "")
        .replace(",", "")
        .strip()
        or None
    )

def main():
    df = pd.read_csv(RAW_FILE, dtype=str)
    print(f"Loaded {len(df)} rows.")

    for col in ["price", "original_price"]:
        df[col] = df[col].apply(clean_currency).astype(float, errors="ignore")

    df["original_price"] = df["original_price"].fillna(df["price"])
    df["shipping"] = df["shipping"].fillna("").astype(str).str.strip()
    df.loc[df["shipping"].eq("") | df["shipping"].eq("N/A"), "shipping"] = "Shipping info unavailable"

    df["discount_percentage"] = ((df["original_price"] - df["price"]) / df["original_price"] * 100).round(2)
    df["discount_percentage"] = df["discount_percentage"].fillna(0)

    df.to_csv(CLEAN_FILE, index=False)
    print(f"✅ Cleaned data saved to {CLEAN_FILE}")

if __name__ == "__main__":
    main()
