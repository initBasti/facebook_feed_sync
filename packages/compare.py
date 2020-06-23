"""
    Author: Sebastian Fricke, Panasiam
    Date: 2020-06-18
    License: GPLv3

    Pull data sources from Plentymarkets and compare them with
    the data pulled from the google sheet.
"""
import re
import difflib
import pandas
import numpy as np

from packages import mappings

def get_attribute(value, value_type):
    """
        Find the value_type inside of the string and return it's value.

        Parameter:
            value [String] : original string ('type:value,type2:value2')
            value_type [String] : type of the value ('color_name', 'size_name')

        Return:
            [String] : value of wanted value_type
                NaN  : not found in original string
    """
    if ',' in value:
        value = value.split(',')
        if value_type in value[0]:
            return value[0].replace(value_type + ':', '')
        return value[1].replace(value_type + ':', '')
    if value_type in value:
        return value.replace(value_type + ':', '')
    return np.nan

def split_attributes(frame, key):
    """
        Split the attributes column into tow columns: color and size.

        Parameter:
            frame [DataFrame]

        Return:
            [DataFrame]
    """
    frame = frame[frame[key].notnull()]
    frame.reset_index(inplace=True, drop=True)
    frame['color'] = frame.apply(lambda x: get_attribute(x[key], 'color_name'),
                                 axis=1)
    frame['size'] = frame.apply(lambda x: get_attribute(x[key], 'size_name'),
                                axis=1)
    return frame.drop(key, 1)

def export_header_check(frame, column):
    """
        Check if the file contains a required column name.

        Parameter:
            frame [DataFrame]
            column [String] : Name of the column header

        Return:
            True/False
    """
    return len(frame.columns[frame.columns.str.contains(pat=column)]) != 0

def read_plenty_export(url, synctype, warehouse):
    """
        Download data from a pre-configured Elastic Export
        format (HTTP). Read the data into a pandas dataframe.

        Parameter:
            url [String] : http url to the specified file
            synctype [String] : Type of sync specified by sub command(argparse)
            warehouse [String] : Name of the warehouse specified in config

        Return:
            [DataFrame] : containing ID(SKU) and value/s
    """
    column_names = mappings.sync_to_gsheet_map[synctype]
    plenty_column = mappings.sync_to_plenty_map[synctype]

    frame = pandas.read_csv(url, sep=';')

    for index, column in enumerate(plenty_column):
        if re.search(r'physicalStock', column):
            plenty_column[index] = column + warehouse
        if not export_header_check(frame=frame, column=column):
            return pandas.DataFrame()

    subset = frame[plenty_column]
    if synctype == 'attr':
        # FIXME key should be pulled from config to stay generic
        subset = split_attributes(
            frame=subset, key='VariationAttributeValues.attributeValues')
    subset.columns = ['Sku'] + ['P_'+x for x in column_names]
    if synctype == 'price':
        subset['P_price'] =\
            subset['P_price'].apply(lambda x: str(f"{x} EUR").replace(".", ","))

    if synctype == 'inventory':
        try:
            subset = subset.astype({'Sku':object, 'P_'+synctype:int})
        except ValueError:
            subset['P_'+synctype] = subset['P_'+synctype]\
                .apply(lambda x: x.replace('.0', ''))
    else:
        for column in column_names:
            subset.astype({'P_'+column:object})
    return subset

def detect_differences(google, plenty, synctype):
    """
        Compare the dataframe from the google sheet and the plenty export.
        Depending on the sync type, the comparission is performed either
        on a single value or on two values.

        Parameter:
            google [DataFrame]
            plenty [DataFrame]
            synctype [String] : Type of sync specified by sub command(argparse)

        Return:
            [DataFrame] merged datframe with items that differ between sources.
    """
    columns = mappings.sync_to_gsheet_map[synctype]
    merge_df = google.merge(plenty, how='left')

    if synctype in ('price', 'inventory'):
        merge_df = merge_df[merge_df['FB_'+columns[0]] !=\
                            merge_df['P_'+columns[0]]]
    elif synctype == 'attr':
        pattern1 = merge_df[merge_df['FB_'+columns[0]] !=\
                            merge_df['P_'+columns[0]]]
        pattern2 = merge_df[merge_df['FB_'+columns[1]] !=\
                            merge_df['P_'+columns[1]]]
        merge_df = pattern1.merge(pattern2, how='outer')
    elif synctype == 'text':
        merge_df.fillna('', inplace=True)
        merge_df['cmp_' + columns[0]] =\
            merge_df.apply(lambda x: difflib.SequenceMatcher(
                None, x['FB_'+columns[0]], x['P_'+columns[0]]).ratio(),
                           axis=1)
        merge_df['cmp_' + columns[1]] =\
            merge_df.apply(lambda x: difflib.SequenceMatcher(
                None, x['FB_'+columns[1]], x['P_'+columns[1]]).ratio(),
                           axis=1)
        merge_df = merge_df[(merge_df['cmp_' + columns[0]] < 0.9989) |\
                            (merge_df['cmp_' + columns[1]] < 0.9989)]
    if synctype == 'inventory':
        merge_df['P_inventory'] = merge_df['P_inventory'].fillna(0).astype(int)
    return merge_df
