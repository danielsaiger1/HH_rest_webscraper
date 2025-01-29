# HH_rest_webscraper

## Webscraper for Restaurants in Hamburg

A simple web scraper designed to retrieve restaurant data in Hamburg, with the possibility of deploying the results in a Flask app.

## Features
- Scrapes restaurant data from a specified source
- Formats and structures the retrieved data
- Can be integrated into a Flask web application for easy deployment

## Requirements
Ensure you have the following dependencies installed:

```bash
pip install -r requirements.txt
```

## Usage

### Load the raw data
To execute the data loader and retrieve the raw data

```bash
python data_loader.py
```

### Process the data
To execute the data processor and transform the data

```bash
python data_processor.py
```


### Deploying with Flask
To serve the data using a Flask application:

```bash
python app.py
```

