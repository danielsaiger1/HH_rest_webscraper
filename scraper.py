from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import requests
from typing import Dict, List, Tuple
import logging

class Scraper:
    def __init__(self, URL, options, driver):
        self.URL = URL
        self.options = options
        self.driver = driver
        
    def create_driver(self):
        options = Options()
        driver = webdriver.Chrome(options=options)
        print("Driver created.")
        return driver
    
    def load_page_raw(self) -> str:
        self.driver = self.create_driver()
        """
        Lädt die Seite und gibt den rohen HTML-Code zurück.
        """
        try:
            if not self.driver:
                self.driver = self.create_driver()
            
            logging.info(f"Lade Seite: {self.URL}")
            self.driver.get(self.URL)
            self.driver.implicitly_wait(10)
            
            # Consent-Banner behandeln
            self._handle_consent_banner()

            # Anzahl der ursprünglichen Divs auf der Seite speichern
            self.initial_divs = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-list-id]')

            # Listings erweitern
            self._expand_listings()
        
            self.page_raw = self.driver.page_source
            logging.info("Seite erfolgreich geladen.")
            return self.page_raw

        except TimeoutException:
            logging.error("Ein Timeout ist aufgetreten.")
            return None

        except Exception as e:
            logging.error(f"Fehler beim Laden der Seite: {e}")
            return None

        finally:
            self._close_driver()
            
            
    def _handle_consent_banner(self):
        try:
            # wait until consent banner is shown
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#usercentrics-root"))
            )
            # deny consent banner
            shadow_host = self.driver.find_element(By.CSS_SELECTOR, "#usercentrics-root")
            shadow_root = shadow_host.shadow_root
            deny_button = shadow_root.find_element(By.CSS_SELECTOR, "button[data-testid='uc-deny-all-button']")
            deny_button.click()
        except:
            print("No consent banner found.")       
    
    def _expand_listings(self):
            # expand listings
            expand_teaser = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ganze Liste anzeigen')]"))
            )
            self.driver.execute_script("arguments[0].click();", expand_teaser)
            
            #sobald sich die Anzahl der Divs ändert wird der HTML Code in page_raw geladen und der driver beendet
            WebDriverWait(self.driver, 10).until(
                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'div[data-list-id]')) > len(self.initial_divs)
            )
            
    def _close_driver(self):
        if self.driver:
            self.driver.quit()
            
    def load_data(self, webpage: str) -> Dict[int, Dict[str, str]]:
        """Parst die Hauptseite und lädt Subpage-Daten parallel."""
        try:
            soup = BeautifulSoup(webpage, "html.parser")
            teaser_list = soup.find("div", class_="teaserList-inline__page")
            if not teaser_list:
                raise ValueError("Keine Teaser-Liste gefunden")

            listings = teaser_list.find_all("article", class_="listTeaser")
            cuisine_types = self._fetch_cuisine_types(webpage)
            restaurants: Dict[int, Dict[str, str]] = {}

            # Subpage-Links sammeln
            links = [
                f"https://www.hamburg-tourism.de{article.find('a', class_='listTeaser__link')['href']}"
                for article in listings
            ]

            # Subpage-Daten parallel laden
            subinfo_results = self.fetch_subinfo(links)

            for idx, (article, subinfo) in enumerate(zip(listings, subinfo_results)):
                name = article.find('h3').text.strip() if article.find('h3') else "N/A"
                description = article.find('p').text.strip() if article.find('p') else "N/A"
                location, sub_link = subinfo

                features = []
                ul = article.find('ul')  
                if ul:
                    list_items = ul.find_all('li')
                    for li in list_items:
                        features.append(li.text.strip())

                cuisine_type = [i for i in features if i in cuisine_types]
                
                rest_type = 'N/A'
                for i in features:
                    if i in ['Restaurant', 'Café/Bistro']:
                        rest_type = i
                        break

                features = [feature for feature in features if feature not in ['Restaurant', 'Café/Bistro', '€€€']]
                features = [feature if feature else "N/A" for feature in features]

                restaurants[idx] = {
                    'name': name,
                    'description': description,
                    'rest_type': rest_type,
                    'cuisine_type': cuisine_type,
                    'location': location,
                    'features': features,
                    'link': links[idx],
                    'sublink': sub_link
                }
                
                print(links[idx])
                
            logging.info("Daten erfolgreich geladen.")
            return restaurants
        
        except Exception as e:
            logging.error(f"Fehler beim Laden der Daten: {e}")
            return {}

    def _fetch_cuisine_types(self, webpage: str) -> List[str]:
        soup = BeautifulSoup(webpage, "html.parser")
        cuisine_inputs = soup.find_all('input', {'type': 'checkbox', 'name': 'filter[cuisinetype][]'})
        cuisine_types = [
            soup.find('label', {'for': elem.get('id')}).text.strip()
            for elem in cuisine_inputs if elem.get('id')
        ]
        return cuisine_types
    
    def fetch_subinfo(self, links: List[str]) -> List[Tuple[str, str]]:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self._get_subinfo, links))
        return results

    def _get_subinfo(self, link: str) -> Tuple[str, str]:
        try:
            response = requests.get(link)
            if response.status_code != 200:
                return "N/A", "N/A"

            soup = BeautifulSoup(response.text, "html.parser")
            contact_block = soup.find('div', class_='contact__address')
            if not contact_block:
                return "N/A", "N/A"

            address = contact_block.find('div', class_='contact__address__informationBundle').get_text(strip=True)
            link_div = contact_block.find('a')
            sub_link = link_div['href'] if link_div else "N/A"

            return address, sub_link
        except Exception as e:
            logging.error(f"Fehler beim Laden der Subpage {link}: {e}")
            return "N/A", "N/A"
        
        
            