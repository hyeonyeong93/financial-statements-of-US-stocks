#!/usr/bin/env python3
import json
import ssl
import certifi
import csv
from urllib.request import urlopen, Request
import os

def get_jsonparsed_data(url):
    context = ssl.create_default_context(cafile=certifi.where())
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    req = Request(url, headers=headers)
    with urlopen(req, context=context) as response:
        data = response.read().decode("utf-8")
    return json.loads(data)

def read_ticker_list(file_path):
    tickers = []
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tickers.append(row['Ticker'])
    return tickers

def save_to_csv(data, file_path):
    if not data:
        print("No data to save.")
        return
    keys = ['symbol', 'price']
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    # Configuration
    base_dir = "/path/to/your/project/directory"
    api_key = 'YOUR_API_KEY'
    base_url = f"https://financialmodelingprep.com/api/v3/stock/full/real-time-price?apikey={api_key}"
    ticker_list_path = os.path.join(base_dir, "ticker-list.csv")
    output_file_path = os.path.join(base_dir, "real_time_stock_prices.csv")

    tickers = read_ticker_list(ticker_list_path)
    tickers_set = set(tickers)

    try:
        data = get_jsonparsed_data(base_url)
        if data:
            filtered_data = [
                {'symbol': item['symbol'], 'price': item['lastSalePrice']}
                for item in data if item['symbol'] in tickers_set
            ]
            save_to_csv(filtered_data, output_file_path)
            print(f"Filtered data has been saved to {output_file_path}")
        else:
            print("No data returned from API.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()