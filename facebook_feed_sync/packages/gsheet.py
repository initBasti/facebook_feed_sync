"""
Synchronize a google sheet with data from PlentyMarkets.
The google sheet is used as a data feed for a facebook product catalog.

Copyright (C) 2020  Sebastian Fricke, Panasiam

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import copy
import gspread
import gspread_dataframe
import pandas
import numpy as np
from loguru import logger

import facebook_feed_sync.packages.plenty as plenty_data


GSHEET_HEADER = [
    'id', 'title', 'description', 'availability', 'inventory',
    'condition', 'price', 'link', 'image_link', 'brand',
    'google_product_category', 'sale_price', 'sale_price_effective_date',
    'item_group_id', 'gender', 'color', 'size', 'age_group', 'material',
    'pattern', 'product_type', 'shipping', 'shipping_weight'
]


def valid_dataframe(parameter: pandas.DataFrame) -> int:
    """ Small wrapper to check if the parameter exists and isn't empty """
    if not isinstance(parameter, pandas.DataFrame):
        return -1

    if len(parameter.index) == 0:
        return 0
    return 1


def gsheet_read(worksheet: gspread.Worksheet) -> pandas.DataFrame:
    """
    Read the specified worksheet directly into a DataFrame
    and remove rows, where no ID is given.
    """

    if not worksheet:
        return pandas.DataFrame()
    dataframe = pandas.DataFrame(worksheet.get_all_records(), dtype=str)
    if len(dataframe.index) == 0:
        return pandas.DataFrame(columns=GSHEET_HEADER)

    # Remove rows where the ID is missing
    empty_rows = dataframe[dataframe['id'] == '']
    if len(empty_rows.index) > 0:
        for row in empty_rows.index:
            worksheet.delete_rows(start_index=row+2)
            dataframe.drop(index=row, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)

    return dataframe


def gsheet_write(worksheet: gspread.Worksheet,
                 dataframe: pandas.DataFrame) -> None:
    """ Update the hosted google sheet with the local dataframe """

    gspread_dataframe.set_with_dataframe(worksheet, dataframe)


def delete_removed_items(google: pandas.DataFrame,
                         plenty: pandas.DataFrame) -> pandas.DataFrame:
    """
    Find & remove rows from the google sheet, where the ID cannot
    be located in PlentyMarkets.

    Parameter:
        google [DataFrame]      -   facebook sync google sheet
        plenty [DataFrame]      -   plentymarkets API data

    Return:
        [DataFrame]             -   updated google sheet
    """
    if valid_dataframe(parameter=google) <= 0:
        return pandas.DataFrame()

    if valid_dataframe(parameter=plenty) <= 0:
        return google

    # ITEMS found in gsheet but not in plenty
    google['delete'] = np.where(~google['id'].isin(plenty['id']), 1, 0)

    indeces = google[google['delete'] == 1].index
    google.drop(indeces, axis=0, inplace=True)

    google.drop('delete', axis=1, inplace=True)
    google.reset_index(drop=True, inplace=True)

    return google


def add_new_items(google: pandas.DataFrame,
                  plenty: pandas.DataFrame) -> pandas.DataFrame:
    """
    Find & add variations from PlentyMarkets to the google sheet,
    which were previously not found in the google sheet.
    Get all data for the new variations from the PlentyMarkets API.

    Parameter:
        google [DataFrame]      -   facebook sync google sheet
        plenty [DataFrame]      -   plentymarkets API data

    Return:
        [DataFrame]             -   updated google sheet
    """
    if valid_dataframe(parameter=plenty) <= 0:
        return google

    # Fill the google sheet with data as it was left empty on purpose
    if len(google.index) == 0 and len(google.columns) == len(GSHEET_HEADER):
        return plenty_data.get_data_from_plentymarkets(
            target=plenty['id'].values)

    # Abort because the google sheet is empty because of an error
    if len(google.index) == 0 and len(google.columns) == 0:
        return pandas.DataFrame()

    plenty_copy = copy.deepcopy(plenty)
    # ITEMS found in plenty but not in gsheet
    plenty_copy['create'] = np.where(~plenty_copy['id'].isin(google['id']),
                                     1, 0)

    new_items = plenty_copy[plenty_copy['create'] == 1]
    if len(new_items.index) == 0:
        return google

    new_items = plenty_data.get_data_from_plentymarkets(
        target=new_items['id'].values)

    return pandas.concat([google, new_items], ignore_index=True)


def update_column(google: pandas.DataFrame,
                  plenty: pandas.DataFrame) -> pandas.DataFrame:
    """
    Update one or more columns with data from PlentyMarkets.

    Parameter:
        google [DataFrame]      -   facebook sync google sheet
        plenty [DataFrame]      -   plentymarkets API data

    Return:
        [DataFrame]             -   updated google sheet
    """
    if valid_dataframe(parameter=google) <= 0:
        return pandas.DataFrame()

    if valid_dataframe(parameter=plenty) <= 0:
        return google

    # abort if any invalid column is detected
    for column in plenty.columns[1:]:
        if column not in GSHEET_HEADER:
            logger.error(f"ERROR: update_column: invalid column {column}")
            return google

    for column in plenty.columns[1:]:
        # Replace each column separatly for each row where the 'id' matches
        merge_frame = google.join(
            plenty[['id', column]].set_index('id'),
            on='id', rsuffix='_plenty')

        google[column] = merge_frame[column + '_plenty']

    return google
