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
    value = (
        str(value)
        .replace("US", "")
        .replace("$", "")
        .replace(",", "")
        .strip()
    )
    # Return None if the cleaned string is not numeric
    return value if value.replace(".", "", 1).isdigit() else None


def main():
    df = pd.read_csv(RAW_FILE, dtype=str)
    print(f"Loaded {len(df)} rows.")

    # Clean and convert numeric columns
    for col in ["price", "original_price"]:
        df[col] = df[col].apply(clean_currency)
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Handle missing values
    df["original_price"] = df["original_price"].fillna(df["price"])
    df["shipping"] = df["shipping"].fillna("").astype(str).str.strip()
    df.loc[df["shipping"].eq("") | df["shipping"].eq("N/A"), "shipping"] = "Shipping info unavailable"

    # Compute discount percentage safely
    df["discount_percentage"] = ((1 - (df["price"] / df["original_price"])) * 100).round(2)
    df["discount_percentage"] = df["discount_percentage"].fillna(0)

    # Save result
    df.to_csv(CLEAN_FILE, index=False)
    print(f"✅ Cleaned data saved to {CLEAN_FILE}")


if __name__ == "__main__":
    main()
