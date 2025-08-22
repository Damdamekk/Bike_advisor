import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_cr():
    """Pobiera dane rowerów ze sklepu CentrumRowerowe.pl"""

    # Konfiguracja przeglądarki
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--ignore-certificate-errors')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    unique_products = set()
    results = []

    for page in range(1, 51):
        url = f'https://www.centrumrowerowe.pl/rowery/?page={page}'
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "real-product")]'))
            )

            products = driver.find_elements(By.XPATH, '//div[contains(@class, "real-product")]')

            for product in products:
                try:
                    link_element = product.find_element(By.XPATH, './/div[contains(@class, "item product")]')
                    link = f"https://www.centrumrowerowe.pl{link_element.get_attribute('data-href')}"
                    if link in unique_products:
                        continue

                    meta_element = product.find_element(By.XPATH, './/input[@name="dataLayerItem"]')
                    product_data = json.loads(meta_element.get_attribute("value"))

                    name = product_data.get("item_name", "Brak nazwy")
                    price = product_data.get("price", "Brak ceny")

                    unique_products.add(link)
                    results.append({
                        "Sklep": "Centrum Rowerowe",
                        "Nazwa": name,
                        "Cena": price,
                        "Link": link
                    })
                except Exception as e:
                    print("Błąd przy pobieraniu danych produktu:", e)

            print(f"Strona {page} przetworzona.")
            time.sleep(2)

        except Exception as e:
            print(f"Błąd ładowania strony {page}: {e}")

    driver.quit()
    return results

if __name__ == "__main__":
    bikes = scrape_cr()
    print(json.dumps(bikes, indent=4, ensure_ascii=False))
