#!/usr/bin/env python3

import pandas as pd
import numpy as np
import os
import time
from filelock import FileLock

def read_csv_with_lock(file_path, max_wait_time=60):
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path, timeout=max_wait_time)

    start_time = time.time()
    while True:
        try:
            with lock:
                print(f"Starting to read file: {file_path}")
                df = pd.read_csv(file_path)
                print(f"Finished reading file: {file_path}")
            return df
        except TimeoutError:
            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"Unable to read file for {max_wait_time} seconds: {file_path}")
            print(f"File is locked. Waiting: {file_path}")
            time.sleep(1)  # Retry every 1 second

def write_csv_with_lock(df, file_path, max_wait_time=60):
    lock_path = file_path + ".lock"
    lock = FileLock(lock_path, timeout=max_wait_time)

    start_time = time.time()
    while True:
        try:
            with lock:
                print(f"Starting to write file: {file_path}")
                df.to_csv(file_path, index=False)
                print(f"Finished writing file: {file_path}")
            return
        except TimeoutError:
            if time.time() - start_time > max_wait_time:
                raise TimeoutError(f"Unable to write file for {max_wait_time} seconds: {file_path}")
            print(f"File is locked. Waiting: {file_path}")
            time.sleep(1)  # Retry every 1 second

# Pandas configuration
pd.set_option('future.no_silent_downcasting', True)

# Set file paths relative to the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
modeled_financial_statements_file = os.path.join(current_dir, 'modeled_financial_statements.csv')
real_time_stock_prices_file = os.path.join(current_dir, 'real_time_stock_prices.csv')
output_file = os.path.join(current_dir, 'FS_with_price.csv')

try:
    # Load CSV files
    print("Starting to read files...")
    modeled_financial_statements_df = read_csv_with_lock(modeled_financial_statements_file)
    real_time_stock_prices_df = read_csv_with_lock(real_time_stock_prices_file)
    print("All files have been read.")

    # Add price column to all rows and set initial value to None
    modeled_financial_statements_df['price'] = None

    # Convert real_time_stock_prices_df to dictionary for faster lookup
    price_dict = dict(zip(real_time_stock_prices_df['symbol'], real_time_stock_prices_df['price']))

    # Add price value to the first row of each symbol
    for symbol in modeled_financial_statements_df['symbol'].unique():
        if symbol in price_dict:
            # Find the index of the first row for the symbol
            first_row_index = modeled_financial_statements_df[modeled_financial_statements_df['symbol'] == symbol].index[0]
            # Add price value
            modeled_financial_statements_df.at[first_row_index, 'price'] = price_dict[symbol]

    # Calculate PBR, PER, PFFO
    def calculate_ratios(row):
        price = row['price']
        if pd.isna(price):
            return pd.Series({'PBR': np.nan, 'PER': np.nan, 'PFFO': np.nan})
        equity_per_share = row['Equity_per_Share']
        eps = row['EPS']
        ffo_per_share = row['FFO_per_Share']
        pbr = price / equity_per_share if equity_per_share != 0 else np.nan
        per = price / eps if eps != 0 else np.nan
        pffo = price / ffo_per_share if ffo_per_share != 0 else np.nan
        return pd.Series({'PBR': pbr, 'PER': per, 'PFFO': pffo})

    # Calculate and add ratios
    modeled_financial_statements_df[['PBR', 'PER', 'PFFO']] = modeled_financial_statements_df.apply(calculate_ratios, axis=1)

    # Round all calculated columns to four decimal places
    columns_to_round = ['EPS', 'FFO_per_Share', 'ROIC', 'ROE', 'CAGR-3-Years', 'CAGR-1-Year',
                        'Interest_Coverage_Ratio', 'Payout_Ratio', 'Equity_per_Share', 
                        'Gross_Profit_per_Share', 'Interest_Expense_per_Share', 
                        'Total_Expense_per_Share', 'Revenue_per_Share', 
                        'Operating_Expense_per_Share', 'Invested_Capital_per_Share',
                        'Current_Asset_per_Share', 'Cash_and_Cash_Equivalent_per_Share',
                        'PBR', 'PER', 'PFFO']
    modeled_financial_statements_df[columns_to_round] = modeled_financial_statements_df[columns_to_round].round(4)

    # Replace inf values with NaN
    modeled_financial_statements_df = modeled_financial_statements_df.replace([np.inf, -np.inf], np.nan)

    # Replace NaN values with empty string
    modeled_financial_statements_df = modeled_financial_statements_df.fillna('')

    # Save the result to a CSV file
    print("Starting to save the result file...")
    write_csv_with_lock(modeled_financial_statements_df, output_file)
    print(f"Processed data has been saved to {output_file}")

    # Print the top 5 rows
    print(modeled_financial_statements_df.head())

except TimeoutError as e:
    print(f"Error: {e}")
    print("Terminating the program.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Terminating the program.")