#!/usr/bin/env python3

import json
import ssl
import certifi
import csv
import os
from urllib.request import urlopen, Request
from datetime import datetime


def get_jsonparsed_data(url, api_key):
    context = ssl.create_default_context(cafile=certifi.where())
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Authorization': f'Bearer {api_key}'
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
            row['Ticker'] = row['Ticker'].replace('/', '.')
            tickers.append(row)
    return tickers


def save_to_csv(data, file_path, mode='w'):
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()

    with open(file_path, mode, newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        if mode == 'w':
            dict_writer.writeheader()
        dict_writer.writerows(data)


def truncate_file(file_path):
    open(file_path, 'w').close()


def main():
    api_key = 'YOUR_API_KEY'
    base_url = "https://financialmodelingprep.com/api/v3/balance-sheet-statement/"
    ticker_list_path = "/path/to/your/ticker-list.csv"
    output_file_path = "/path/to/your/output/all_balance_sheets.csv"

    # Truncate the output file before starting
    truncate_file(output_file_path)

    tickers = read_ticker_list(ticker_list_path)

    for index, ticker_info in enumerate(tickers):
        ticker = ticker_info['Ticker']
        url = f"{base_url}{ticker}?period=quarter&limit=80&apikey={api_key}"

        try:
            data = get_jsonparsed_data(url, api_key)

            if data:
                # Sort data by date to ensure the most recent quarter is first
                data.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)

                # Mark the most recent quarter
                data[0]['is_recent_quarter'] = True

                # Add additional information to each data point
                for item in data:
                    item.update({
                        'Company Name': ticker_info['Company Name'],
                        'Market Cap': ticker_info['Market Cap'],
                        'Country': ticker_info['Country'],
                        'Sector': ticker_info['Sector'],
                        'Industry': ticker_info['Industry'],
                        'is_recent_quarter': item.get('is_recent_quarter', False)
                    })
                    item.pop('link', None)
                    item.pop('finalLink', None)

            # Write to CSV (append mode for all except the first ticker)
            mode = 'w' if index == 0 else 'a'
            save_to_csv(data, output_file_path, mode)
            print(f"Balance sheet data for {ticker} has been saved.")
        except Exception as e:
            print(f"An error occurred while processing {ticker}: {e}")

    print(f"All balance sheet data has been saved to {output_file_path}")


if __name__ == "__main__":
    main()