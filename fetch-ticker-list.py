#!/usr/bin/env python3
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def download_google_sheet(spreadsheet_id, range_name, credentials_path, output_path):
    # Authenticate and create the Sheets API service
    creds = Credentials.from_service_account_file(credentials_path, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API to get the data
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(values[1:], columns=values[0])

    # Save the DataFrame as a CSV file
    df.to_csv(output_path, index=False)
    print(f"Data has been saved to {output_path}")

def main():
    # Set up the parameters
    spreadsheet_id = 'YOUR_SPREADSHEET_ID'
    range_name = 'YOUR_RANGE_NAME'
    credentials_path = '/path/to/your/credentials.json'
    output_path = '/path/to/your/output.csv'

    # Download the Google Sheet
    download_google_sheet(spreadsheet_id, range_name, credentials_path, output_path)

if __name__ == '__main__':
    main()