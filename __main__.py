import configparser
import argparse
import pandas
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def get_google_credentials():
    """
        Check if the token.pickle file contains valid credentials
        if that is not the case get them manually.
        TODO: find method for cronjob to notify administrator about
        problem.

        Return:
            [Google Sheet credentials]
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def read_google_sheet(creds, sheet_id, sheet_range):
    """
        Open the sheet with the @sheet_id, check if the column names
        are as expected, pull the data and transform to pandas dataframe.

        Parameter:
            creds [Google Sheet credentials]
            sheet_id [String] : Identification of the google sheet
            sheet_range [String] : ColumnRow combination, specifies the area of
                                   values (exp: A1:E2 -> A1, A2, B1 .. E1, E2)

        Return:
            [DataFrame] : containing ID(SKU) and storage amount
    """
    service = build('sheets', 'v4', credentials=creds)
    sheet_list = []
    row_count = 0

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=sheet_range).execute()
    values = result.get('values', [])

    if not values:
        print('No data found')
    else:
        for row in values:
            if row_count == 0:
                if not row[0] == 'id' or not row[4] == 'inventory':
                    print('Wrong data format. ')
                    print("requires: 'A' == 'id', 'E' == 'inventory'")
                    print(f"actual: 'A' == {row[0]}, 'E' == {row[4]}")
                    return pandas.DataFrame()
            else:
                if not row[0]:
                    continue
                sheet_list.append([row[0], row[4]])
            row_count += 1

    return pandas.DataFrame(sheet_list, columns=['Sku', 'Inventory'])

def write_google_sheet(sheet_range):
    """
        Enter a specific value to column:row coordinate.

        Parameter:
            sheet_range [String] : ColumnRow combination, specifies the area of
                                   values (exp: A1:E2 -> A1, A2, B1 .. E1, E2)

        Return:
            [Bool] True success / False failure
    """

def export_header_check(frame, sku_column, stock_column):
    """
        Check if the file contains the required column names.
        Detect any typo within the config 'plenty_warehouse' entry.

        Parameter:
            frame [DataFrame]
            sku_column [String] : Name of the sku_column
            stock_column [String] : Name of the stock_column

        Return:
            True/False
    """
    if not frame.columns[frame.columns.str.contains(pat=sku_column)]:
        return False
    if not frame.columns[frame.columns.str.contains(pat=stock_column)]:
        similar = frame.filter(regex='VariationStock.physicalStock').columns
        if similar:
            print("No column found for warehouse: {0}, did you mean: {1}?"
                  .format(warehouse,
                          similar.replace('VariationStock.physicalStock',
                                          '', 1)))
        else:
            print("File requires a physicalStock column, see README.md")
        return False
    return True

def read_plenty_export(url, warehouse):
    """
        Download storage amount data from a pre-configured Elastic Export
        format (HTTP). Read the data into a pandas dataframe.

        Parameter:
            url [String] : http url to the specified file

        Return:
            [DataFrame] : containing ID(SKU) and storage amount
    """
    frame = pandas.read_csv(url, sep=';')

    sku_column = 'Variation.number'
    stock_column = 'VariationStock.physicalStock.' + warehouse
    if not export_header_check(frame=frame, sku_column=sku_column,
                               stock_column=stock_column):
        return pandas.DataFrame()



def clean_numeric_value(series):
    """
        Remove any unwanted separators and transform to a integer.

        Parameter:
            series [Series] : Pandas series of values to be cleaned

        Return:
            [Series] : series with clean values
    """

def main():
    """
        Functionality:
            Download the data from Plentymarkets by accessing the pre-configured
            Elastic Export HTTP URL

            Read in the google sheet.

            read data from a specific column for all IDs
            compare with values from Plentymarkets Export and

            return Dictionary of IDs together with the values of the column
            where the values did not match.

            Replace the values of the specific column for every ID
            within the dictionary.

            Return if the dictionary is empty

    """
    creds = None
    url = str()

    config = configparser.ConfigParser().read('config.ini')

    if config['General']['google_sheet_rows']:
        sheet_range = 'A1:E' + config['General']['google_sheet_rows']
    else:
        sheet_range = 'A1:E20'
        print("No specified amount of rows to read, default to range: {0}"
              .format(sheet_range))
        print("Check the config.ini file to adjust the range")

    creds = get_google_credentials()

    g_df = read_google_sheet(
        creds=creds, sheet_id=config['General']['google_sheet_id'],
        sheet_range=sheet_range)

    p_df = read_plenty_export(url=config['General']['plenty_url'],
                              warehouse=config['General']['plenty_warehouse'])

if __name__ == '__main__':
    main()
