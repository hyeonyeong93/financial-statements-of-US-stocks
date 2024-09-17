#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

def load_data(file_path):
    return pd.read_csv(file_path)

def preprocess_data(df):
    if 'finalLink' in df.columns:
        df = df.rename(columns={'finalLink': 'SEC_filing'})
    df['interestExpense'] = df['interestExpense'].abs()
    return df

def calculate_eps(df):
    df['EPS'] = df['netIncome'] / df['weightedAverageShsOut']
    return df

def calculate_ffo(df):
    df['FFO'] = df['netIncome'] + df['depreciationAndAmortization']
    df['FFO_per_Share'] = df['FFO'] / df['weightedAverageShsOut']
    return df

def calculate_roic(df):
    df['tax_rate'] = df['incomeTaxExpense'] / df['incomeBeforeTax']
    df['nopat'] = df['operatingIncome'] * (1 - df['tax_rate']) * 4
    df['invested_capital'] = df['totalDebt'] + df['totalStockholdersEquity']
    df['ROIC'] = df['nopat'] / df['invested_capital']
    return df

def calculate_roe(df):
    df['ROE'] = (df['netIncome'] * 4) / df['totalStockholdersEquity']
    return df

def calculate_cagr(start_value, end_value, years):
    return (end_value / start_value) ** (1/years) - 1

def calculate_3year_cagr(series):
    if len(series) < 12:
        return None
    start_value = series.iloc[-1]
    end_value = series.iloc[0]
    return calculate_cagr(start_value, end_value, 3)

def calculate_1year_cagr(series):
    if len(series) < 4:
        return None
    start_value = series.iloc[-1]
    end_value = series.iloc[0]
    return calculate_cagr(start_value, end_value, 1)

def calculate_cagr_metrics(df):
    df['Revenue_per_Share'] = df['revenue'] / df['weightedAverageShsOut']
    df['CAGR-3-Years'] = df.groupby('symbol')['Revenue_per_Share'].rolling(window=12, min_periods=12).apply(calculate_3year_cagr, raw=False).reset_index(0, drop=True)
    df['CAGR-3-Years'] = df.groupby('symbol')['CAGR-3-Years'].shift(-11)
    df['CAGR-1-Year'] = df.groupby('symbol')['Revenue_per_Share'].rolling(window=4, min_periods=4).apply(calculate_1year_cagr, raw=False).reset_index(0, drop=True)
    df['CAGR-1-Year'] = df.groupby('symbol')['CAGR-1-Year'].shift(-3)
    return df

def calculate_interest_coverage_ratio(df):
    df['EBITDA'] = df['operatingIncome'] + df['depreciationAndAmortization']
    df['Interest_Coverage_Ratio'] = np.where(df['interestExpense'] != 0,
                                             df['EBITDA'] / df['interestExpense'],
                                             None)
    return df

def calculate_additional_metrics(df):
    df['Payout_Ratio'] = df['dividendsPaid'].abs() / df['netIncome'].abs()
    df['Equity_per_Share'] = df['totalStockholdersEquity'] / df['weightedAverageShsOut']
    df['Gross_Profit_per_Share'] = df['grossProfit'] / df['weightedAverageShsOut']
    df['Interest_Expense_per_Share'] = df['interestExpense'] / df['weightedAverageShsOut']
    df['Total_Expense_per_Share'] = (df['costOfRevenue'] + df['operatingExpenses']) / df['weightedAverageShsOut']
    df['Operating_Expense_per_Share'] = df['operatingExpenses'] / df['weightedAverageShsOut']
    df['Number_of_Shares_Outstanding'] = df['weightedAverageShsOut']
    df['Invested_Capital_per_Share'] = df['invested_capital'] / df['weightedAverageShsOut']
    df['Current_Asset_per_Share'] = df['totalCurrentAssets'] / df['weightedAverageShsOut']
    df['Cash_and_Cash_Equivalent_per_Share'] = df['cashAndCashEquivalents'] / df['weightedAverageShsOut']
    df['Total_Debt_per_Share'] = df['totalDebt'] / df['weightedAverageShsOut']
    df['Current_Liabilities_per_Share'] = df['totalCurrentLiabilities'] / df['weightedAverageShsOut']
    return df

def round_columns(df):
    columns_to_round = ['EPS', 'FFO_per_Share', 'ROIC', 'ROE', 'CAGR-3-Years', 'CAGR-1-Year',
                        'Interest_Coverage_Ratio', 'Payout_Ratio', 'Equity_per_Share', 
                        'Gross_Profit_per_Share', 'Interest_Expense_per_Share', 
                        'Total_Expense_per_Share', 'Revenue_per_Share', 
                        'Operating_Expense_per_Share', 'Invested_Capital_per_Share',
                        'Current_Asset_per_Share', 'Cash_and_Cash_Equivalent_per_Share',
                        'Total_Debt_per_Share', 'Current_Liabilities_per_Share']
    df[columns_to_round] = df[columns_to_round].round(4)
    return df

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, 'financial_statements.csv')
    output_file = os.path.join(current_dir, 'modeled_financial_statements.csv')

    df = load_data(input_file)
    df = preprocess_data(df)
    df = calculate_eps(df)
    df = calculate_ffo(df)
    df = calculate_roic(df)
    df = calculate_roe(df)
    df = calculate_cagr_metrics(df)
    df = calculate_interest_coverage_ratio(df)
    df = calculate_additional_metrics(df)
    df = round_columns(df)

    results = df[['symbol', 'date', 'calendarYear', 'period', 'SEC_filing',
                  'EPS', 'FFO_per_Share', 'ROIC', 'ROE', 'CAGR-3-Years', 'CAGR-1-Year',
                  'Interest_Coverage_Ratio', 'Payout_Ratio', 'Equity_per_Share', 
                  'Gross_Profit_per_Share', 'Interest_Expense_per_Share', 
                  'Total_Expense_per_Share', 'Revenue_per_Share', 
                  'Operating_Expense_per_Share', 'Number_of_Shares_Outstanding',
                  'Invested_Capital_per_Share', 'Current_Asset_per_Share',
                  'Cash_and_Cash_Equivalent_per_Share',
                  'Total_Debt_per_Share', 'Current_Liabilities_per_Share']]

    print(results.head())
    results.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()