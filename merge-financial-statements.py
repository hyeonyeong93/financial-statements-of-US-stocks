#!/usr/bin/env python3

import pandas as pd
import os

def remove_columns(df, columns_to_remove):
    return df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors='ignore')

def main():
    # File paths
    cash_flow_path = "/path/to/your/all_cash_flow_statements.csv"
    balance_sheet_path = "/path/to/your/all_balance_sheets.csv"
    income_statement_path = "/path/to/your/all_income_statements.csv"
    output_path = "/path/to/your/output/merged_financial_statements.csv"

    # Columns to remove from cash flow and balance sheet
    columns_to_remove = [
        'link', 'finalLink', 'is_recent_quarter'
    ]

    # Columns to remove from all dataframes
    columns_to_remove_all = ['cik', 'fillingDate', 'acceptedDate']

    # Columns to move right after 'symbol'
    columns_to_move = ['reportedCurrency', 'calendarYear', 'period']

    # Read CSV files
    cf_df = pd.read_csv(cash_flow_path)
    bs_df = pd.read_csv(balance_sheet_path)
    is_df = pd.read_csv(income_statement_path)

    # Remove specified columns from cash flow and balance sheet dataframes
    cf_df = remove_columns(cf_df, columns_to_remove)
    bs_df = remove_columns(bs_df, columns_to_remove)

    # Remove specified columns from all dataframes
    cf_df = remove_columns(cf_df, columns_to_remove_all)
    bs_df = remove_columns(bs_df, columns_to_remove_all)
    is_df = remove_columns(is_df, columns_to_remove_all)

    # Merge dataframes
    merged_df = pd.merge(cf_df, bs_df, on=['symbol', 'date'] + columns_to_move, suffixes=('_cf', '_bs'))
    merged_df = pd.merge(merged_df, is_df, on=['symbol', 'date'] + columns_to_move, suffixes=('', '_is'))

    # Reorder columns
    cols = merged_df.columns.tolist()
    new_cols = ['symbol'] + columns_to_move + [col for col in cols if col not in ['symbol'] + columns_to_move]
    merged_df = merged_df[new_cols]

    # Save merged dataframe to CSV
    merged_df.to_csv(output_path, index=False)
    print(f"Merged financial statements saved to {output_path}")

if __name__ == "__main__":
    main()