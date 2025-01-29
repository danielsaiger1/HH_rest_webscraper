from scraper import Scraper
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from datetime import datetime
import json
import os

class Dataloader:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_data(self, URL):
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")  # reduces logs to WARN and ERROR 
            
            driver = webdriver.Chrome(options=options)
            scraper = Scraper(URL, options, driver)
            
            try:
                html = scraper.load_page_raw()
                data = scraper.load_data(html)
                return data
            finally:
                driver.quit()  # Ensure the driver is closed
        except WebDriverException as e:
            print(f"WebDriver error: {e}")
            return None
        except Exception as e:
            print(f"An error occurred while scraping: {e}")
            return None

    def save_data(self, input_data):
        try:
            if input_data is None:
                print("No data to save.")
                return
            
            today = datetime.today().strftime('%Y%m%d')
            
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                
            file_path = os.path.join(self.output_dir, f'{today}_output_data.json')
            
            with open(file_path, 'w') as f:
                json.dump(input_data, f)
            
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"An error occurred while saving data: {e}")

def main():
    with open("config/dt/config.json", 'r') as config_file:
        config = json.load(config_file)
        
    URL = config.get('URL')
    output_dir = config.get('output_dir')
    
    loader = Dataloader(output_dir) 

    print("Starting data processing...")
    restaurant_data = loader.get_data(URL)

    if restaurant_data:
        print("Data successfully retrieved.")
        loader.save_data(restaurant_data)
    else:
        print("Failed to retrieve data.")
    
if __name__ == "__main__":
    main()
