"""
    Author: Sebastian Fricke, Panasiam
    Date: 2020-06-23
    License: GPLv3

    Read and write data from/to the google sheets API.
"""
import os
import pickle
import pandas
import numpy as np

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from packages import log
from packages import mappings

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def find_valid_rows(data):
    """
        Check the data set for empty rows and return a list of indeces to
        existing rows.

        Parameter:
            data [Dict] : Dictionary from the google sheet API response

        Return:
            [List] : indeces of existing rows
    """
    indeces = []
    sku_col = {}
    for column in data:
        if column['values'][0][0] == 'id':
            sku_col = column
            break

    if not sku_col:
        print(f"Error: No 'id' column found within the google sheet")
        return indeces

    for index, item in enumerate(sku_col['values'][1:]):
        if len(item) > 0:
            indeces.append(index+1)
        else:
            print(f"Not a valid row: @{index} {item}")

    return indeces

def align_columns(data):
    """
        Google sheets cut of empty values if no actual value exists
        from the last value until the end.
        Example:
        If the last actual value of a column is on line 120, but the document
        contains 150 rows, in that case google sheets will return 120 rows.
        But a pandas dataframe requires all lists for the dataframe creation
        to be of the same size.

        Parameter:
            data [Dict] : Dictionary of containing the values read from the
                          Google API

        Return:
            [Dict] : with appended empty values
    """
    max_len = len(data['Sku'])
    for key in data:
        if len(data[key]) < max_len:
            data[key] += ['' for x in range(max_len - len(data[key]))]
        elif len(data[key]) > max_len:
            data[key].pop()

    return data

def build_sheet_range(column, max_row, range_column=''):
    """
        Specify the area within the google sheet used for reading/writing.

        Parameters:
            column [String] : Start column on the sheet ('A', 'B' etc.)
            max_row [Integer] : Amount of rows for the range
            range_column [String] : End column on the sheet
                                (To create a horizontal-vertical range (A1:E2))

        Return:
            [String] - Example: 'A1:E5' (A1, A2, ... , E4, E5)
    """
    if max_row:
        if not range_column:
            return str(f'{column}1:{column}{max_row}')
        return str(f'{column}1:{range_column}{max_row}')
    print("No specified amount of rows to read, default to range: {0}"
          .format('A1:E20'))
    print("Check the config.ini file to adjust the range")
    return 'A1:E20'

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

def read_google_sheet(creds, sheet_id, max_row, synctype):
    """
        Open the sheet with the @sheet_id, check if the column names
        are as expected, pull the data and transform to pandas dataframe.

        Parameter:
            creds [Google Sheet credentials]
            sheet_id [String] : Identification of the google sheet
            max_row [String] : Amount of rows to take into the range
            synctype [String] : Type of the sync (Argparse option)

        Return:
            [DataFrame] : containing ID(SKU) and specified column
    """
    service = build('sheets', 'v4', credentials=creds)
    sheet_dict = {}
    removed_index = []
    sheet_range = [build_sheet_range(column='A', max_row=max_row)]

    names = mappings.sync_to_gsheet_map[synctype]
    columns = mappings.sync_to_gsheet_range_map[synctype]
    index = mappings.sync_to_gsheet_index_map[synctype]
    index.append(0)

    if len(columns) == 1:
        sheet_range.append(build_sheet_range(column=columns[0],
                                             max_row=max_row))
    else:
        for column in columns:
            sheet_range.append(build_sheet_range(column=column,
                                                 max_row=max_row))

    sheet = service.spreadsheets()
    result = sheet.values().batchGet(spreadsheetId=sheet_id,
                                     ranges=sheet_range).execute()
    ranges = result['valueRanges']
    if not ranges:
        print('No data found')

    indeces = find_valid_rows(data=ranges)
    if not indeces:
        return pandas.DataFrame()

    for data in ranges:
        values = data['values']
        column_name = values[0][0]
        if column_name in names:
            indeces_copy = indeces.copy()
            while len(values) - 1 < max(indeces_copy):
                removed_index.append(indeces_copy.pop())
            sheet_dict['FB_' + column_name] =\
                [values[x][0] if values[x] else '' for x in indeces_copy]
            for _ in removed_index:
                sheet_dict['FB_' + column_name].append('')
        elif column_name == 'id':
            sheet_dict['Sku'] = [values[x][0] for x in indeces if values[x][0]]
        else:
            print("Range mapping is deprecated: {0} not found in {1}"
                  .format(column_name, ['id'] + names))
    sheet_dict['FB_index'] = indeces

    sheet_dict = align_columns(data=sheet_dict)

    frame = pandas.DataFrame(sheet_dict)
    if synctype == 'inventory':
        try:
            frame = frame.astype({'Sku':object, 'FB_'+synctype:int})
        except ValueError:
            frame['FB_'+synctype] =\
                frame['FB_'+synctype].apply(lambda x: x.replace('.0', ''))
    else:
        for name in names:
            frame.astype({'FB_'+name:object})

    return frame

def write_google_sheet(creds, sheet_id, frame, key, column):
    """
        Enter a specific value to column:row coordinate.

        Parameter:
            creds [Google Sheet credentials]
            sheet_id [String] : Identification of the google sheet
            frame [DataFrame] : difference between source and target
            key [String]      : header name of the column to update

        Return:
            [Bool] True success / False failure/empty
    """
    data = []
    data_cols = ['range', 'values']

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    generator = frame.iterrows()
    for item in generator:
        # dataframe is 0 indexed and skip header row => +2
        try:
            range_name = column + str(item[1]['FB_index']+1)
        except KeyError:
            print(f"Invalid key for write_google_sheet: {key}")
            return False
        values = [[str(item[1]['P_' + key]).replace(str(np.nan), '')]]
        data.append(dict(zip(data_cols, [range_name, values])))

    body = {'valueInputOption': 'RAW', 'data':data}
    response = sheet.values().batchUpdate(
        spreadsheetId=sheet_id, body=body).execute()

    if not 'totalUpdatedRows' in response.keys():
        return False

    return True
