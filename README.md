# Assignment-5


# COSC 482 – Lab Assignment 5: eBay Tech Deals Pipeline

### 🧩 Objective
End-to-end data pipeline that scrapes, cleans, and analyzes **eBay Global Tech Deals**.

### ⚙️ Components
1. **scraper.py** – Collects live product data using Selenium and saves to `ebay_tech_deals.csv`.
2. **.github/workflows/scraper.yml** – Runs scraper automatically every 3 hours.
3. **clean_data.py** – Cleans and transforms raw data, computing discount %.
4. **EDA.ipynb** – Performs exploratory analysis and visualizations.

### 🧠 Key Insights
- Most deals appear during mid-day hours.
- Average discounts range ≈ 15 – 30 %.
- Apple / Samsung / Laptop are most frequent keywords.
- “Free shipping” dominates other options.

### 🚧 Challenges
- Lazy-loading elements required repeated scrolling.
- Shipping info not always visible; handled via fallbacks.

### 💡 Future Improvements
- Add multi-category scraping (Home, Fashion etc.).
- Integrate sentiment or keyword trend analysis.
