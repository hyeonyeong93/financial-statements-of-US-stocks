#!/usr/bin/env python3
import csv
import requests
import time
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Load API key from environment variable
API_KEY = os.environ.get("FINANCIAL_MODELING_PREP_API_KEY")

# Google Sheets API settings
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
CREDS_JSON = os.environ.get("GOOGLE_SHEETS_CREDS_PATH")
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
SHEET_NAME = 'EMA'

def preprocess_ticker(ticker):
    """Preprocess the ticker symbol."""
    return ticker.replace('/', '.')

def get_ema_data(ticker, period):
    """Fetch EMA data for the given ticker and period."""
    processed_ticker = preprocess_ticker(ticker)
    url = f"https://financialmodelingprep.com/api/v3/technical_indicator/daily/{processed_ticker}?period={period}&type=ema&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            return float(data[0]['ema'])
        else:
            print(f"No data found for: {processed_ticker}, period: {period}")
            return None
    except requests.RequestException as e:
        print(f"API request error ({processed_ticker}, period: {period}): {e}")
        return None

def is_uptrend(ema_100, ema_400):
    """Check if it's an uptrend by comparing EMA_100 and EMA_400."""
    return ema_100 > ema_400

def process_tickers(input_file, output_file):
    """Process the list of tickers from the input file and save results to the output file and Google Sheets."""
    # Google Sheets authentication and worksheet opening
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    
    # Clear existing data
    sheet.clear()
    
    # Add headers
    headers = ['Ticker', 'Date', 'EMA_100', 'EMA_400', 'is_uptrend']
    sheet.append_row(headers)

    results = []
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        writer.writerow(headers)
        
        # Skip header row
        next(reader)
        
        for row in reader:
            if row:  # Skip empty rows
                ticker = row[0]  # Get ticker symbol from the first column
                print(f"Processing: {ticker}")
                
                ema_100 = get_ema_data(ticker, 100)
                time.sleep(0.5)  # Wait 0.5 seconds between API requests
                ema_400 = get_ema_data(ticker, 400)
                
                if ema_100 is not None and ema_400 is not None:
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    uptrend = is_uptrend(ema_100, ema_400)
                    result_row = [ticker, current_date, ema_100, ema_400, uptrend]
                    writer.writerow(result_row)
                    results.append(result_row)
                
                time.sleep(0.5)  # Wait 0.5 seconds before processing the next ticker

    # Upload results to Google Sheets in one batch
    sheet.append_rows(results)
    print(f"Data successfully uploaded to Google Sheets.")

# Main execution part
if __name__ == "__main__":
    input_file = "ticker-list.csv"
    output_file = "ema_results.csv"
    
    start_time = time.time()
    process_tickers(input_file, output_file)
    end_time = time.time()
    
    print(f"Processing completed. Results saved to ema_results.csv file and Google Sheets.")
    print(f"Total execution time: {end_time - start_time:.2f} seconds")