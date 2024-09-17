#!/usr/bin/env python3
import csv
import requests
from datetime import datetime
import time
import pandas as pd
import os

# Load API key from environment variable
API_KEY = os.environ.get("FINANCIAL_MODELING_PREP_API_KEY")
BASE_URL = "https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{ticker}?apikey={api_key}"

def fetch_dividend_data(ticker):
    url = BASE_URL.format(ticker=ticker, api_key=API_KEY)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'historical' in data:
            print(f"  Successfully fetched data for {ticker}.")
            return data['historical']
    print(f"  Failed to fetch data for {ticker}.")
    return []

def classify_dividend_frequency(sub_df):
    if len(sub_df) < 2:
        return False  # Not enough data to determine
    date_diff = (sub_df['Date'].iloc[0] - sub_df['Date'].iloc[1]).days
    if date_diff < 60:
        return True
    return False

def calculate_annual_dividend(dividend_data, is_monthly):
    if dividend_data.empty:
        return 0
    latest_dividend = dividend_data['Dividend'].iloc[0]
    if is_monthly:
        return latest_dividend * 12
    else:
        return latest_dividend * 4  # Assume quarterly if not monthly

def main():
    print("Starting to fetch and process dividend data for all tickers...")
    
    # Read all tickers from ticker-list.csv file
    with open('ticker-list.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        tickers = [row[0] for row in reader]
    
    print(f"Processing a total of {len(tickers)} tickers.")

    all_data = []
    for i, ticker in enumerate(tickers, 1):
        print(f"\nProcessing ticker {i}/{len(tickers)}: {ticker}")
        dividend_data = fetch_dividend_data(ticker)
        if dividend_data:
            for item in dividend_data:
                all_data.append({
                    'Ticker': ticker,
                    'Date': datetime.strptime(item['date'], "%Y-%m-%d"),
                    'Dividend': item['dividend']
                })
            print(f"  Processed {len(dividend_data)} dividend records for {ticker}.")
        else:
            print(f"  No dividend data found for {ticker}.")
        
        time.sleep(0.5)  # Wait 0.5 seconds between API requests
        
        # Show progress
        if i % 10 == 0 or i == len(tickers):
            print(f"Progress: {i}/{len(tickers)} tickers processed ({i/len(tickers)*100:.2f}%)")

    df = pd.DataFrame(all_data)
    if not df.empty:
        df_sorted = df.sort_values(['Ticker', 'Date'], ascending=[True, False])
        for ticker in tickers:
            ticker_data = df_sorted[df_sorted['Ticker'] == ticker]
            if not ticker_data.empty:
                recent_2_records = ticker_data.head(2)
                is_monthly = classify_dividend_frequency(recent_2_records)
                df.loc[df['Ticker'] == ticker, 'is_Monthly_dividend'] = is_monthly
                annual_dividend = calculate_annual_dividend(ticker_data, is_monthly)
                df.loc[df['Ticker'] == ticker, 'Annual_Dividend'] = annual_dividend
            else:
                print(f"  No data for {ticker}.")

        print("\nSaving results to dividend_data.csv file...")
        df.to_csv('dividend_data.csv', index=False)
        print("Data fetching and processing completed. Results saved to dividend_data.csv file.")
        print(f"Processed data for a total of {len(df['Ticker'].unique())} tickers.")

        monthly_dividend_tickers = df[df['is_Monthly_dividend'] == True]['Ticker'].unique()
        print(f"\nNumber of monthly dividend tickers: {len(monthly_dividend_tickers)}")
        print(f"List of monthly dividend tickers: {monthly_dividend_tickers.tolist()}")
    else:
        print("No data to process.")

if __name__ == "__main__":
    main()