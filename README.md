# Ozon Smartphone Scraper (Selenium)

Demo Selenium scraper for Ozon smartphones category:
- collects product links from the listing
- opens each product page
- extracts title, prices, image and selected characteristics
- saves results to JSON

## Features
- Random User-Agent rotation
- Scrolling + explicit waits (WebDriverWait)
- Extracts key characteristics (RAM, storage, CPU, screen, cameras, battery, etc.)
- Saves data to `ozon_smartphone_data.json`

## Tech Stack
Python • Selenium • webdriver-manager

## Setup
### 1) Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

#Install dependencies
pip install -r requirements.txt

#Run
python src/scraper.py


After run, output file:

ozon_smartphone_data.json

#Configuration

Inside src/scraper.py you can change:

url — category page

LIMIT — number of products to parse

SELECTORS — CSS selectors for title/price/image/characteristics

KEY_FEATURES — which characteristics to keep

USER_AGENTS — list of UA strings

#Notes

Ozon may change HTML structure or apply anti-bot protections.
If selectors stop working, update SELECTORS and/or add more realistic delays/proxy.

This repo is a template/demo for scraping logic, not a production-ready crawler.
