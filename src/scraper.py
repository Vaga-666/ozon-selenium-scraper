import json
import random
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка Selenium
chrome_options = Options()
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]
chrome_options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
logging.info("Браузер запущен")

url = "https://www.ozon.ru/category/smartfony-15502/"
driver.get(url)
time.sleep(random.uniform(5, 10))

SELECTORS = {
    "title": "h1[class*='tsHeadline']",
    "price_current": ".c3025-a0 .tsHeadline500Medium",
    "price_old": ".c3025-a0 .tsBodyControl400Small",
    "image": "div[data-widget='webGallery'] img",
    "characteristics": "div[data-widget='webCharacteristics'] div"  # Оставляем div
}

KEY_FEATURES = [
    "Оперативная память", "Встроенная память", "Процессор", "Диагональ экрана",
    "Разрешение экрана", "Технология матрицы", "Емкость аккумулятора",
    "Разрешение основной камеры", "Разрешение фронтальной камеры", "Число ядер процессора"
]

# Функция для фильтрации характеристик
def filter_characteristics(chars):
    filtered = []
    seen = set()
    for char in chars:
        # Разделяем текст на строки
        lines = char.split('\n')
        for i in range(len(lines) - 1):
            key = lines[i].strip()
            value = lines[i + 1].strip()
            # Проверяем, является ли key одной из целевых характеристик
            if any(feature in key for feature in KEY_FEATURES) and value and value not in KEY_FEATURES:
                combined = f"{key}: {value}"
                if combined not in seen:
                    filtered.append(combined)
                    seen.add(combined)
    return filtered

def parse_smartphone_links():
    links = set()
    for _ in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(3, 5))

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget='searchResultsV2']"))
        )
        items = driver.find_elements(By.CSS_SELECTOR, "div[data-widget='searchResultsV2'] a[href*='/product/']")
        for item in items:
            link = item.get_attribute("href")
            if link and "product" in link:
                links.add(link)
                logging.info(f"Найдена ссылка: {link}")
    except Exception as e:
        logging.error(f"Ошибка при ожидании ссылок: {e}")
        logging.info(f"HTML страницы: {driver.page_source[:2000]}...")

    return list(links)

def get_product_data(product_url):
    driver.get(product_url)
    time.sleep(random.uniform(5, 10))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)

    try:
        title = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["title"]))
        ).text
    except Exception as e:
        logging.warning(f"Ошибка при загрузке названия: {e}")
        title = "Не найдено"

    try:
        price_current = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["price_current"]))
        ).text
    except Exception as e:
        logging.warning(f"Ошибка при загрузке текущей цены: {e}")
        price_current = "Не найдено"

    try:
        price_old = driver.find_element(By.CSS_SELECTOR, SELECTORS["price_old"]).text
    except:
        price_old = "Нет данных"

    try:
        image = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["image"]))
        )
        image_url = image.get_attribute("src")
    except Exception as e:
        logging.warning(f"Ошибка при загрузке изображения: {e}")
        image_url = "Не найдено"

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-widget='webCharacteristics']"))
        )
        characteristics_elements = driver.find_elements(By.CSS_SELECTOR, SELECTORS["characteristics"])
        characteristics_text = [elem.text.strip() for elem in characteristics_elements if elem.text.strip()]
        logging.info(f"Сырые характеристики: {characteristics_text}")
        filtered_characteristics = filter_characteristics(characteristics_text)
        if not filtered_characteristics:
            logging.warning("Характеристики пусты после фильтрации")
    except Exception as e:
        logging.warning(f"Ошибка при загрузке характеристик: {e}")
        filtered_characteristics = []

    return {
        "Название": title,
        "Цена текущая": price_current,
        "Цена старая": price_old,
        "Изображение": image_url,
        "Характеристики": filtered_characteristics
    }

logging.info("Начинаем парсинг ссылок на смартфоны...")
smartphone_links = parse_smartphone_links()
logging.info(f"Найдено ссылок: {len(smartphone_links)}")

LIMIT = 8
smartphone_links = smartphone_links[:LIMIT]
logging.info(f"Ограничение на парсинг: {LIMIT} ссылок")

products = []
for link in smartphone_links:
    logging.info(f"Парсим товар: {link}")
    product_data = get_product_data(link)
    products.append(product_data)

with open("ozon_smartphone_data.json", "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=4)
logging.info("Данные сохранены в ozon_smartphone_data.json")

driver.quit()
logging.info("Браузер закрыт")
