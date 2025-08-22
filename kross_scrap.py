import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_kross():
    """Pobiera dane rowerów ze sklepu Kross"""

    # Konfiguracja przeglądarki
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--ignore-certificate-errors')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    results = []
    unique_links = set()

    for page in range(1, 7):
        url = f'https://kross.eu/pl/rowery?page={page}'
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "c-offerBox is-lazyLoadHovered")]'))
            )

            products = driver.find_elements(By.XPATH, '//div[contains(@class, "c-offerBox is-lazyLoadHovered")]')

            for product in products:
                try:
                    meta = product.find_element(By.XPATH, './/meta[@data-analytics-product="true"]')
                    product_data = json.loads(meta.get_attribute("data-analytics-item"))

                    name = product_data.get("name", "Brak nazwy")
                    price = product_data.get("price", "Brak ceny")

                    link_element = product.find_element(By.XPATH, './/a[contains(@class, "a-typo") and contains(@data-analytics-on, "click")]')
                    link = link_element.get_attribute("href")

                    if link in unique_links:
                        continue

                    unique_links.add(link)
                    results.append({
                        "Sklep": "Kross",
                        "Nazwa": name,
                        "Cena": price,
                        "Link": link
                    })

                except Exception as e:
                    print("Błąd przy parsowaniu produktu:", e)

            print(f"Strona {page} przetworzona.")
            time.sleep(2)

        except Exception as e:
            print(f"Błąd ładowania strony {page}: {e}")

    driver.quit()
    return results

if __name__ == "__main__":
    bikes = scrape_kross()
    print(json.dumps(bikes, indent=4, ensure_ascii=False))
