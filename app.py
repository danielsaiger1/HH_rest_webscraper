from flask import Flask, render_template
import json
import os
from datetime import datetime

app = Flask(__name__)

today = datetime.today().strftime('%Y%m%d')
    
file_path = f'./api/data/{today}_data_transformed.json'

with open(file_path, 'r') as file:
    data = json.load(file)


@app.route('/')
def index():
    return render_template('index.html', restaurants=data)

@app.route('/restaurants')
def restaurants():
    # Hier geben wir die Daten an das HTML Template weiter
    return render_template('restaurants.html', restaurants=data)

if __name__ == '__main__':
    app.run(debug=True)
