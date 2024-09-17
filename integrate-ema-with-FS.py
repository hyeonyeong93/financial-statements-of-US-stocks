#!/usr/bin/env python3
import pandas as pd

def merge_financial_data():
    # Read ema_results.csv file
    ema_df = pd.read_csv('ema_results.csv')

    # Read FS_with_price.csv file
    fs_df = pd.read_csv('FS_with_price.csv')

    # Convert Ticker and is_uptrend to dictionary
    uptrend_dict = dict(zip(ema_df['Ticker'], ema_df['is_uptrend']))

    # Add is_uptrend column and initialize
    fs_df['is_uptrend'] = ''

    # Add is_uptrend value only to the first row for each symbol
    for symbol in fs_df['symbol'].unique():
        # Find rows corresponding to the symbol
        mask = fs_df['symbol'] == symbol
        # Index of the first row for the symbol
        first_row_index = fs_df.loc[mask].index[0]
        # Find is_uptrend value for the symbol in uptrend_dict
        if symbol in uptrend_dict:
            fs_df.loc[first_row_index, 'is_uptrend'] = uptrend_dict[symbol]

    # Read dividend_data.csv file
    dividend_df = pd.read_csv('dividend_data.csv')

    # Select only the most recent dividend info for each ticker
    latest_dividend_info = dividend_df.groupby('Ticker').first().reset_index()

    # Merge dividend info into FS_with_price.csv
    fs_df = fs_df.merge(latest_dividend_info[['Ticker', 'is_Monthly_dividend', 'Annual_Dividend']],
                        left_on='symbol', right_on='Ticker', how='left')

    # Remove unnecessary 'Ticker' column after merging
    fs_df = fs_df.drop(columns=['Ticker'])

    # Save the result to FS_with_price.csv file
    fs_df.to_csv('FS_with_price.csv', index=False)

    print("Processing completed. FS_with_price.csv file has been updated with EMA and dividend information.")

if __name__ == "__main__":
    merge_financial_data()