import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_intersport():
    """Pobiera dane rowerów ze sklepu Intersport"""

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
    url = "https://www.intersport.pl/sporty/rowery/rowery/"

    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "listingBox")]'))
        )
        products = driver.find_elements(By.XPATH, '//div[contains(@class, "listingBox")]')

        for product in products:
            try:
                name_element = product.find_element(By.XPATH, './/a[contains(@class, "productLink lbTitle")]')
                name = name_element.text.strip()
                link = name_element.get_attribute("href")

                if link in unique_links:
                    continue
                unique_links.add(link)

                try:
                    price_element = product.find_element(By.XPATH, './/span[contains(@class, "lbPricePromo")]/span[@class="amount"]')
                except:
                    price_element = product.find_element(By.XPATH, './/div[contains(@class, "lbPriceRegular")]/span[@class="amount"]')

                price = price_element.text.strip().replace(",", ".")

                results.append({
                    "Sklep": "Intersport",
                    "Nazwa": name,
                    "Cena": price,
                    "Link": link
                })

            except Exception as e:
                print("Błąd przy parsowaniu produktu:", e)

    except Exception as e:
        print("Błąd ładowania strony Intersport:", e)

    driver.quit()
    return results

if __name__ == "__main__":
    bikes = scrape_intersport()
    print(json.dumps(bikes, indent=4, ensure_ascii=False))
