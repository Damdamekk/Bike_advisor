import json
from cr_scrap import scrape_cr
from interSport_scrap import scrape_intersport
from kross_scrap import scrape_kross

def get_all_bikes():
    """ Pobiera dane rowerów z wszystkich skryptów """
    bikes = []
    
    # Scrapowanie rowerów z różnych stron
    bikes.extend(scrape_cr())  # CentrumRowerowe.pl
    bikes.extend(scrape_intersport())  # Intersport
    #bikes.extend(scrape_kross())  # Kross
    
    return bikes

def save_to_file(data, filename="wyniki.json"):
    """ Zapisuje dane do pliku JSON """
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f"Wyniki zapisane do pliku: {filename}")

if __name__ == "__main__":
    all_bikes = get_all_bikes()
    save_to_file(all_bikes)

