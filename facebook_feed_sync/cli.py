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
import string
import configparser
import argparse
import os
import os.path
import sys
import gspread
import plenty_api
from loguru import logger

import facebook_feed_sync.packages.shared_data as shared
from facebook_feed_sync.packages import gsheet, plenty


PROG_NAME = 'facebook_feed_sync'
USER = os.getlogin()
if sys.platform == 'linux':
    BASE_PATH = os.path.join(
        '/', 'home', str(f'{USER}'), '.config', PROG_NAME
    )
elif sys.platform == 'win32':
    BASE_PATH = os.path.join(
        'C:\\', 'Users', str(f'{USER}'), '.config', PROG_NAME
    )
if not os.path.exists(BASE_PATH):
    os.mkdir(BASE_PATH)

CONFIG_PATH = os.path.join(BASE_PATH, 'config.ini')


HEADER_SYNC_MAP = {
    'inventory':    ['inventory'],
    'price':        ['price'],
    'text':         ['title', 'description'],
    'attribute':    ['color', 'size'],
    'link':         ['link', 'image_link'],
    'all':          gsheet.GSHEET_HEADER
}


def setup_argparser():
    """
    Return:
        [Argparse Object]
    """
    parser = argparse.ArgumentParser(prog=PROG_NAME)
    parser.add_argument('--verbose', '-v', required=False,
                        help='Add messages to explain what the program does',
                        action='store_true', dest='verbose')
    parser.add_argument('--type', '-t', '--sync',
                        help="Choose the synchronization method",
                        choices=['inventory', 'price', 'attribute',
                                 'text', 'link', 'all'],
                        dest='synctype',
                        required=False)

    namespace = parser.parse_args()
    return namespace


def get_image_match_criteria(value: str) -> dict:
    if not value or not isinstance(value, str):
        return {}

    if value.find(';') == -1:
        logger.error("Image match criteria type and value need to be "
                     "separated by a ';'")
        return {}

    try:
        crit_type = value.split(';')[0]
        crit_value = value.split(';')[1]
    except IndexError:
        logger.error("Invalid config value for 'image_match_criteria'\n"
                     f"=> {value}")
        return {}

    return {'type': crit_type, 'value': crit_value}


def check_config(config: configparser.ConfigParser) -> bool:
    """
    Check if the configuration has the correct structure and
    minimum requirments.
    """
    missing_section = string.Template(
        "Configuration requires the $section section."
    )
    missing_option = string.Template(
        "Configuration requires the $option option"
        " within the $section section."
    )
    for section in ['General', 'Mapping']:
        if not config.has_section(section):
            logger.error(missing_section.substitute(section=section))
            return False
        if section == 'General':
            options = ['google_sheet_id', 'plenty_api_url', 'lang']
        else:
            options = ['facebook_referrer', 'image_match_criteria',
                       'item_name_number', 'gender_item_property',
                       'age_item_property', 'url_variation_property',
                       'google_product_category_item_property',
                       'sales_price_id', 'main_warehouse',
                       'color_attribute_id', 'size_attribute_id',
                       'material_variation_property']
        for option in options:
            if not config.has_option(section=section, option=option):
                logger.error(missing_option.substitute(option=option,
                                                section=section))
                return False

    if (not config['General']['google_sheet_id'] or
            not config['General']['plenty_api_url']):
        logger.error("Google sheet ID and Plentymarkets url required.")
        return False

    return True


def get_config_values(config: configparser.ConfigParser) -> bool:
    """ Check for missing required values in the configuration """
    shared.lang = config['General']['lang']
    if not shared.lang:
        shared.lang = 'de'

    msg = string.Template(
        "No value for $field given, abort."
    )

    variable_config_mapping = {
        'facebook_referrer': 'referrer',
        'image_match_criteria': 'img_match_criteria',
        'item_name_number': 'item_name_number',
        'gender_item_property': 'gender_property_id',
        'age_item_property': 'age_property_id',
        'url_variation_property': 'url_property_id',
        'material_variation_property': 'material_property_id',
        'google_product_category_item_property': 'google_category_property_id',
        'sales_price_id': 'price_id',
        'main_warehouse': 'warehouse_id',
        'color_attribute_id': 'color_attribute_id',
        'size_attribute_id': 'size_attribute_id'
    }

    # Set the shared_data values and abort if any of them is missing
    for key in variable_config_mapping:
        if key == 'image_match_criteria':
            criteria = get_image_match_criteria(value=config['Mapping'][key])
            if not criteria:
                logger.error(msg.substitute(field=key))
                return False
            setattr(shared, variable_config_mapping[key], criteria)
            continue

        setattr(shared, variable_config_mapping[key], config['Mapping'][key])
        if not getattr(shared, variable_config_mapping[key]):
            logger.error(msg.substitute(field=key))
            return False

    if int(getattr(shared, 'item_name_number')) not in [1, 2, 3]:
        logger.error("item_name_number can allow be 1, 2 or 3."
                     f"[is {getattr(shared, 'item_name_number')}]")
        return False

    return True


def cli():
    parser = setup_argparser()
    verbose = logger.info if parser.verbose else lambda *a, **k: None

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if not check_config(config=config):
        sys.exit(1)

    api = plenty_api.PlentyApi(base_url=config['General']['plenty_api_url'],
                               use_keyring=True, data_format='json')

    if not get_config_values(config=config):
        logger.error("Invalid configuration.")
        sys.exit(1)

    if not parser.synctype:
        logger.error("Specify the sync type: [inventory, price, text, "
                     "attribute, link, all].")
        sys.exit(1)

    verbose("Load the google-sheet and get the first sheet.")
    google_account = gspread.oauth()
    sheet = google_account.open_by_key(config['General']['google_sheet_id'])
    worksheet = sheet.get_worksheet(0)

    verbose("Read the google-sheet.")
    google = gsheet.gsheet_read(worksheet=worksheet)

    verbose("Get all Plentymarkets variations through the API.")
    variations = api.plenty_api_get_variations(
        refine={'referrerId': config['Mapping']['facebook_referrer'],
                'isActive': True},
        additional=['properties', 'images', 'variationAttributeValues',
                    'stock', 'variationSalesPrices'],
        lang=shared.lang
    )
    if not variations:
        sys.exit(1)
    variations = [var for var in variations if not var['isMain']]
    shared.plenty_variations = variations
    shared.plenty_api_instance = api

    verbose("Fetch necessary data for the specified sync type.")
    sync = plenty.get_data_from_plentymarkets(
        header=HEADER_SYNC_MAP[parser.synctype])

    verbose("Check if new variations were added in Plentymarkets.")
    google = gsheet.add_new_items(google=google, plenty=sync)
    verbose("Check if variations were deleted in PlentyMarkets.")
    google = gsheet.delete_removed_items(google=google, plenty=sync)
    verbose("Update the columns of the google-sheet.")
    google = gsheet.update_column(google=google, plenty=sync)

    if len(google.index) > 0:
        verbose("Write the changes to the google-sheet.")
        gsheet.gsheet_write(worksheet=worksheet, dataframe=google)
        verbose("Resize the google-sheet to it's current size.")
        worksheet.resize(rows=len(google.index))
