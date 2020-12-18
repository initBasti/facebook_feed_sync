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
import pandas
from loguru import logger

import facebook_feed_sync.packages.shared_data as shared
import facebook_feed_sync.packages.gsheet as gsheet


ITEM_TYPE_COLUMNS = ['title', 'description', 'google_product_category',
                     'gender', 'age_group', 'brand']
ATTRIBUTE_TYPE_COLUMNS = ['color', 'size']
VALID_ATTRIBUTE_TYPES = ['color', 'size']
VALID_VARIATION_PROPERTIES = ['url', 'material']
VALID_ITEM_PROPERTIES = ['gender', 'age', 'google_category']
VALID_TEXT_TYPES = ['name1', 'name2', 'name3', 'description']


class ColumnValuesFiller():
    """
    Fetch the correct values from PlentyMarkets for a facebook catalog column.

    Map every column of the facebook catalog to a method of this class.
    The method returns the corresponding values for all variations, which
    were declared within the class initialization.

    Build match-tables to simplify access to item, attribute and brand related
    information, while reducing the API calls at the same time.
    """
    def __init__(self, variations: list, header: list):
        """
        Create the match-tables with the given columns and variations.

        Parameter:
            variations  [list]  -   list of variation IDs
                                    (variation number in PlentyMarkets)
            header      [list]  -   list of facebook catalog column names
        """
        self.variations: list = variations
        self.header: list = header
        self.plenty = shared.plenty_api_instance
        self.inventory: list = []
        self.match_item: dict = {}
        self.match_brand: dict = {}
        self.match_attribute: dict = {}
        self.matchtables = self.build_matchtables()

    def get_value(self, name: str) -> list:
        default = 'invalid column'
        return getattr(self, str(name) + '_value', lambda: default)()

    def id_value(self) -> list:
        return [x['number'] for x in self.variations]

    def title_value(self) -> list:
        name = 'name' + str(shared.item_name_number)
        return self.get_text_values(field=name)

    def description_value(self) -> list:
        return self.get_text_values(field='description')

    def inventory_value(self) -> list:
        if not self.inventory:
            self.inventory = self.get_inventory_values()
        return self.inventory

    def availability_value(self) -> list:
        if not self.inventory:
            self.inventory = self.get_inventory_values()
        return [availability_message(x) for x in self.inventory]

    def condition_value(self) -> list:
        return ['new' for x in self.variations]

    def price_value(self) -> list:
        return self.get_price_values()

    def link_value(self) -> list:
        return self.get_variation_property_values(property_type='url')

    def image_link_value(self) -> list:
        return self.get_image_url_value()

    def brand_value(self) -> list:
        return [self.match_brand[str(x['itemId'])] for x in self.variations]

    def google_product_category_value(self) -> list:
        return self.__get_item_property_values(property_type='google_category')

    def sale_price_value(self) -> list:
        return self.empty_values()

    def sale_price_effective_date_value(self) -> list:
        return self.empty_values()

    def item_group_id_value(self) -> list:
        return [str(x['itemId']) for x in self.variations]

    def gender_value(self) -> list:
        return self.__get_item_property_values(property_type='gender')

    def color_value(self) -> list:
        return self.get_attribute_values(attribute_type='color')

    def size_value(self) -> list:
        return self.get_attribute_values(attribute_type='size')

    def age_group_value(self) -> list:
        return self.__get_item_property_values(property_type='age')

    def material_value(self) -> list:
        return self.get_variation_property_values(property_type='material')

    def pattern_value(self) -> list:
        return self.empty_values()

    def product_type_value(self) -> list:
        return self.empty_values()

    def shipping_value(self) -> list:
        return self.empty_values()

    def shipping_weight_value(self) -> list:
        return [str(f"{x['weightG']} g") for x in self.variations]

    def empty_values(self) -> list:
        return ['' for x in self.variations]

    def build_attribute_map(self) -> dict:
        attributes = self.plenty.plenty_api_get_attributes(
            additional=['values'])
        if not attributes:
            logger.error("ERROR: get attributes request to the PlentyMarkets"
                         " API failed!")
        for attribute in attributes:
            self.match_attribute.update({str(attribute['id']): {}})
            for val in attribute['values']:
                value = ''
                for name in val['valueNames']:
                    if name['lang'].lower() == shared.lang:
                        value = name['name']
                self.match_attribute[
                    str(attribute['id'])].update({str(val['id']): value})

    def build_matchtables(self) -> bool:
        """
        Create a match table to quickly locate corresponding data.

        Fetch the data from Plentymarkets in order to create a:
        Variation to item map, Item to manufacturer map and
        attribute value to attribute value ID map.

        Return:
            [bool]                  -   Return False if any API call failed.
        """
        if any(item in self.header for item in ITEM_TYPE_COLUMNS):
            items = self.plenty.plenty_api_get_items(
                additional=['itemProperties'], lang=shared.lang)
            if not items:
                logger.error("ERROR: get item request to the PlentyMarkets API"
                             " failed!")
                return False

            for var in self.variations:
                self.match_item.update({str(var['id']): x for x in items
                                        if x['id'] == var['itemId']})
            if 'brand' in self.header:
                manufact = self.plenty.plenty_api_get_manufacturers()
                if not manufact:
                    logger.error("ERROR: get manufacturers request to the"
                                 " PlentyMarkets API failed!")
                    return False
                for item in items:
                    self.match_brand.update(
                        {str(item['id']): x['name'] for x in manufact
                         if x['id'] == item['manufacturerId']})

        if any(item in self.header for item in ATTRIBUTE_TYPE_COLUMNS):
            self.build_attribute_map()
        return True

    def get_text_values(self, field: str) -> list:
        """
        Get the text value for either the name or the description.

        Fetch the text in the configured language and leave the field
        empty if the language value is not present.

        Parameter:
            field [str]             -   Name of the key in the item texts
                                        field of the API response

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        if field not in VALID_TEXT_TYPES:
            return []
        for variation in self.variations:
            text = self.match_item[str(variation['id'])]['texts'][0]
            if text['lang'].lower() == shared.lang:
                column.append("".join(text[field].splitlines()))
            else:
                column.append('')
        return column

    def get_attribute_values(self, attribute_type: str) -> list:
        """
        Get the attribute value for the configured attributes [Color, Size].

        Parameter:
            attribute_type [str]     -   first part of the variable name
                                         found in the shared module.

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        if attribute_type not in VALID_ATTRIBUTE_TYPES:
            logger.error(f"ERROR: invalid attribute type {attribute_type}")
            return []

        attribute_id: int = getattr(shared, attribute_type + '_attribute_id')
        for variation in self.variations:
            if 'variationAttributeValues' not in variation.keys():
                logger.error("ERROR: variations without attribute data.")
                return []
            value = ''
            val_id = 0
            for attribute in variation['variationAttributeValues']:
                if attribute['attributeId'] == int(attribute_id):
                    val_id = attribute['valueId']
            if val_id:
                value = self.match_attribute[str(attribute_id)][str(val_id)]
            column.append(value)
        return column

    def get_inventory_values(self) -> list:
        """
        Get the stock for each variation from the configured warehouse.

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        for variation in self.variations:
            if 'stock' not in variation.keys():
                logger.error("ERROR: variations without stock data.")
                return []
            value = 0
            for stock in variation['stock']:
                if stock['warehouseId'] == int(shared.warehouse_id):
                    value = stock['netStock']
            column.append(str(value))
        return column

    def get_price_values(self) -> list:
        """
        Get the price which is available for the facebook referrer.

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        for variation in self.variations:
            if 'variationSalesPrices' not in variation.keys():
                logger.error("ERROR: variations without price data.")
                return []
            value = 0
            for price in variation['variationSalesPrices']:
                if price['salesPriceId'] == int(shared.price_id):
                    value = price['price']
            if value == 0:
                logger.error(f"ERROR: variation {variation['id']} has no price"
                             f" with price ID: {shared.price_id}")
                return []
            column.append(to_euro(value))
        return column

    def __get_item_property_values(self, property_type: str) -> list:
        """
        Get the property value for one of the specified variation properties.

        Fetch the value for the language which was assigned to the
        @shared.lang variable through the configuration file. If no
        value is found for the desired language leave the field empty.

        Parameter:
            property_type [str]     -   first part of the variable name
                                        found in the shared module.

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        if property_type not in VALID_ITEM_PROPERTIES:
            logger.error(f"ERROR: invalid item property type {property_type}")
            return []

        prop_id: int = getattr(shared, property_type + '_property_id')
        for variation in self.variations:
            value = ''
            try:
                props = self.match_item[str(variation['id'])]['itemProperties']
            except KeyError:
                logger.error("ERROR: missing item properties from get_items"
                             " API response")
                return []
            for prop in props:
                if not prop['propertyId'] == int(prop_id):
                    continue
                if ('propertySelectionId' in prop.keys() and
                        prop['propertySelectionId']):
                    value = self.__get_item_property_from_selection_list(
                        item_property=prop)
                elif prop['valueTexts']:
                    value = self.__get_item_property_from_text_values(
                        item_property=prop, property_type=property_type)
            if property_type == 'age' and not value:
                value = 'Adult'
            column.append(value)
        return column

    def __get_item_property_from_selection_list(self,
                                                item_property: dict) -> str:
        for select in item_property['propertySelection']:
            if select['id'] == item_property['propertySelectionId']:
                continue
            if select['lang'] == shared.lang:
                return select['name']
        return ''

    def __get_item_property_from_text_values(self,
                                             item_property: dict,
                                             property_type: str) -> str:
        # check if the desired language value exists
        langs = [x['lang'].lower() for x in item_property['valueTexts']]
        if shared.lang not in langs:
            return ''

        for text in item_property['valueTexts']:
            if property_type == 'age':
                if text['lang'].lower() == 'en':
                    if text['value'].lower() not in ['adult', 'child']:
                        # default to Adult if no valid value is found
                        value = 'Adult'
                    value = text['value']
            if text['lang'].lower() == shared.lang:
                value = text['value']
        return value

    def get_variation_property_values(self, property_type: str) -> list:
        """
        Get the property value for one of the specified variation properties.

        Fetch the value for the language which was assigned to the
        @shared.lang variable through the configuration file. If no
        value is found for the desired language leave the field empty.

        The only exception to this rule is the url property, which uses
        the first available language if the desired is not found.
        FIX? If this is a problem for you contact me or send in a patch.

        Parameter:
            property_type [str]     -   first part of the variable name
                                        found in the shared module.

        Return:
            [list]                  -   value for every variation
        """
        column = []
        if property_type not in VALID_VARIATION_PROPERTIES:
            logger.error("ERROR: invalid variation property type "
                         f"{property_type}")
            return []

        prop_id: int = getattr(shared, property_type + '_property_id')
        for variation in self.variations:
            if 'properties' not in variation.keys():
                logger.error("ERROR: variations without property data.")
                return []
            value = ''
            for prop in variation['properties']:
                # check if the desired language value exists
                langs = [x['lang'].lower() for x in prop['relationValues']]
                if shared.lang not in langs:
                    if property_type != 'url' or not langs:
                        continue
                    lang_choice = langs[0]
                else:
                    lang_choice = shared.lang

                if prop['propertyId'] == int(prop_id):
                    for rel_val in prop['relationValues']:
                        if rel_val['lang'].lower() == lang_choice:
                            value = rel_val['value']
            column.append(value)
        return column

    def get_image_url_value(self) -> list:
        """
        Get the first image of every variation which is available for
        the Facebook referrer.

        Return:
            [list]                  -   value for every variation
        """
        column: list = []
        for variation in self.variations:
            if 'images' not in variation.keys():
                logger.error("ERROR: variations without image data.")
                return []
            value = ''
            img = get_first_picture(images=variation['images'])
            if img:
                for avail in img['availabilities']:
                    match_type = shared.img_match_criteria['type']
                    match_value = shared.img_match_criteria['value']
                    if (avail['type'] == match_type and
                            avail['value'] == int(match_value)):
                        value = img['url']
            column.append(value)
        return column


def get_data_from_plentymarkets(header: list = None,
                                target: list = None) -> pandas.DataFrame:
    """
        Fetch data from plentymarkets for a specific subset of the
        google sheet columns.

        Parameter:
            header  [list]      -   google sheet header subset
            target  [list]      -   List of variation IDs to fetch for

        Return:
                    [DataFrame] -   variation ID and matching values
                                    for all variations with the given
                                    referrer ID.
    """
    columns: dict = {}

    variations = copy.deepcopy(shared.plenty_variations)
    if ((target is None or len(target) == 0) and
            (header is None or len(header) == 0)):
        return pandas.DataFrame()
    if target is not None and len(target) > 0:
        variations = [var for var in variations if var['number'] in target]
        if len(variations) == 0:
            return pandas.DataFrame()

    if header is None or len(header) == 0:
        header = gsheet.GSHEET_HEADER

    if any(item not in gsheet.GSHEET_HEADER for item in header):
        logger.error("ERROR: invalid column name/s:"
                     f"{[x for x in header if x not in gsheet.GSHEET_HEADER]}")
        return pandas.DataFrame()

    if 'id' not in header:
        header = ['id'] + header

    column_value_filler = ColumnValuesFiller(variations=variations,
                                             header=header)
    if not column_value_filler.matchtables:
        return pandas.DataFrame()

    for col in header:
        columns[col] = column_value_filler.get_value(name=col)

    return pandas.DataFrame.from_dict(columns)


def availability_message(stock: int) -> str:
    if int(stock) > 0:
        return "in stock"
    return "out of stock"


def to_euro(price: float):
    """ Turn the price in to the accepted format: [{EUR},{CENT} {CURRENCY}]"""
    euro: int = price // 1
    cent: int = price - euro
    return str(f"{int(euro)},{int(cent*100):02} EUR")


def get_first_picture(images: list) -> dict:
    min_pos = -1
    if not images:
        return {}

    for img in images:
        if min_pos == -1 or img['position'] < min_pos:
            min_pos = img['position']

    for img in images:
        if img['position'] == min_pos:
            return img

    return {}
