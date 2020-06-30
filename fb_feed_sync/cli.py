"""
    Author: Sebastian Fricke
    Date: 2020-06-17
    License: GPLv3

    Synchronize specific columns of a google sheet with data from a
    plentymarkets elastic export. The google sheet is then used as
    a data feed for a facebook product catalog.
"""
import configparser
import argparse
import os
import os.path
import sys
from datetime import datetime

from fb_feed_sync.packages import google_sheet, compare, mappings, log

DATA_DIR = os.path.join('/usr', 'local', 'data')
CONFIG_PATH = os.path.join(DATA_DIR, 'config.ini')

def clean_log_folder(log_folder):
    '''
        Remove all change record from the previous day.

        parameter:
            log_folder [String] : Location specified in the configuration
    '''
    log_files = []

    if not log_folder:
        return
    for files in os.walk(log_folder):
        log_files = files[2]

    for log in log_files:
        try:
            log_date = datetime.strptime(log, "%d-%M-%Y.log")
        except ValueError:
            continue
        if log_date < datetime.now():
            os.remove(os.path.join(log_folder, log))

def record_changes(frame, key, log_folder):
    """
        Enter the performed changes by `write_google_sheet` into a log file.

        Parameter:
            frame [DataFrame] - pandas dataframe containing the inventory
                                of source and target
    """
    if not log_folder:
        return
    if not os.path.exists(log_folder):
        os.mkdir(log_folder)
    today = datetime.now().strftime('%d-%m-%Y')
    log_file = os.path.join(log_folder, today + '.log')

    with open(log_file, mode='a') as item:
        now = datetime.now().strftime("%H:%M")
        item.write(str(f"Summary [{now}] sync:{key}:\n"))
        gen = frame.iterrows()

        for row in gen:
            if key == 'description':
                try:
                    item.write(str("{0}. {1}... -> {2}...\n"
                                   .format(row[1]['Sku'],
                                           row[1]['FB_'+key][:40],
                                           row[1]['P_'+key][:40])))
                except TypeError:
                    item.write(str("{0}. {1}... -> {2}...\n"
                                   .format(row[1]['Sku'], row[1]['FB_'+key],
                                           row[1]['P_'+key])))
            else:
                item.write(str("{0}.{1} -> {2}\n"
                               .format(row[1]['Sku'], row[1]['FB_' + key],
                                       row[1]['P_' + key])))

def setup_stock_sync():
    config_key = 'inventory_plenty_url'
    sync_key = 'inventory'
    return [config_key, sync_key]

def setup_price_sync():
    config_key = 'price_plenty_url'
    sync_key = 'price'
    return [config_key, sync_key]

def setup_text_sync():
    config_key = 'text_plenty_url'
    sync_key = 'text'
    return [config_key, sync_key]

def setup_attr_sync():
    config_key = 'attr_plenty_url'
    sync_key = 'attr'
    return [config_key, sync_key]

def setup_argparser():
    """
        Setup the parser for the different sub-commands.

        Return:
            [Argparse Object]
    """
    parser = argparse.ArgumentParser(prog='fb_feed_sync')
    subparser = parser.add_subparsers(
        title="sync options",
        description="read the README, which contains the requirments")

    stock = subparser.add_parser('inventory',
                                 help='inventory sync plenty->facebook')
    stock.set_defaults(func=setup_stock_sync)
    price = subparser.add_parser('price', help='price sync plenty->facebook')
    price.set_defaults(func=setup_price_sync)
    attr = subparser.add_parser('attribute',
                                help='initial upload of attributes')
    attr.set_defaults(func=setup_attr_sync)
    text = subparser.add_parser('text', help='sync of title & description')
    text.set_defaults(func=setup_text_sync)

    return parser

def main():
    """
        Functionality:
            Download the data from Plentymarkets by accessing the
            pre-configured Elastic Export HTTP URL

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

    export_link = ''
    synctype = []

    parser = setup_argparser()
    try:
        export_link, synctype = parser.parse_args().func()
    except AttributeError:
        print("No sync type specified, see fb_feed_sync --help")

    if not export_link or not synctype:
        print("Specify the sync type: [stock, price, text, attr].")
        sys.exit(0)

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    clean_log_folder(log_folder=config['General']['log-path'])
    mappings.log_location = config['General']['log-path']

    creds = google_sheet.get_google_credentials()

    g_df = google_sheet.read_google_sheet(
        creds=creds, sheet_id=config['General']['google_sheet_id'],
        max_row=config['General']['google_sheet_rows'],
        synctype=synctype)
    if len(g_df.index) == 0:
        log.update_log(
            error=str('Empty google data from sheet: {0}'
                      .format(config['General']['google_sheet_id']),
            log_folder=config['General']['log_path']))

    p_df = compare.read_plenty_export(
        url=config['General'][export_link], synctype=synctype,
        warehouse=config['General']['plenty_warehouse'])
    if len(p_df.index) == 0:
        log.update_log(
            error=str('Empty plentymarkets export data from URL: {0}'
                      .format(config['General'][export_link]),
            log_folder=config['General']['log_path']))


    difference = compare.detect_differences(google=g_df, plenty=p_df,
                                            synctype=synctype)

    if len(difference.index) == 0:
        sys.exit(0)

    for key, column in zip(mappings.sync_to_gsheet_map[synctype],
                           mappings.sync_to_gsheet_range_map[synctype]):
        if (google_sheet.write_google_sheet(
                creds=creds, sheet_id=config['General']['google_sheet_id'],
                frame=difference, key=key, column=column)):
            record_changes(frame=difference, key=key,
                           log_folder=config['General']['log-path'])
