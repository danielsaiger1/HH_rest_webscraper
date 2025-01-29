from datetime import datetime
import pandas as pd
import json
from json import loads, dumps
import re
import os

class Dataprocessor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
    
    def load_data(self):
        today = datetime.today().strftime('%Y%m%d')
        try:
            with open(f"{self.input_path}/{today}_output_data.json", 'r') as f:
                self.data = json.load(f)
                print("Data loaded successfully")
                return self.data
        except Exception as e:
            print(f"Data not found. Error: {e}")
            return None
    
    def json_to_df(self, data_input):
        records = []
        for item in data_input.items():
            records.append(item[1])
        self.dataframe = pd.DataFrame(records)
        return self.dataframe
    
    def split_address(self, address):
        # Regex für Adresse, die Hausnummer und PLZ zusammen enthält
        pattern = r"^(.*?)(\d{1,3}[a-zA-Z]?)\s+(\d{5})\s+(.*)$"
        match = re.match(pattern, address)
        if match:
            street = match.group(1).strip()
            house_number = match.group(2)
            postal_code = match.group(3)
            city = match.group(4).strip()
            return pd.Series([street, house_number, postal_code, city])
        else:
            return pd.Series([None, None, None, None])

    def transform_addresses(self, df):
        # Wendet split_address auf jede Zeile der 'location'-Spalte an und gibt die neuen Spalten zurück
        df[['street', 'house_number', 'postal_code', 'city']] = df['location'].apply(
            lambda loc: self.split_address(loc)
        )
        df = df.drop(columns=['location'])
        return df

    def save_data(self, input_data):
        try:
            if input_data is None:
                print("No data to save.")
                return
            
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)
                
            today = datetime.today().strftime('%Y%m%d')
            file_path = os.path.join(self.output_path, f'{today}_data_transformed.json')
            
            with open(file_path, 'w') as f:
                json.dump(input_data, f)  # Ensures pretty printing of the JSON data
            
            print(f"Data successfully saved to {file_path}")
        except Exception as e:
            print(f"An error occurred while saving data: {e}")
    
            
def main():
    with open("config/dt/config.json", 'r') as config_file:
        config = json.load(config_file)
        
    input_path_read = config.get('input_path_read')
    output_path_write = config.get('output_path_write')
    
    processor = Dataprocessor(input_path_read, output_path_write)
    
    data_raw = processor.load_data()
    
    df = processor.json_to_df(data_raw)
    
    df = processor.transform_addresses(df)
    
    json_output = loads(df.to_json(orient="records"))
    
    processor.save_data(json_output)
    
    print(df.head())

if __name__ == "__main__":
    main()
