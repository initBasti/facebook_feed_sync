import pytest
import unittest.mock
import pandas
from pandas.testing import assert_frame_equal
import plenty_api


from facebook_feed_sync.packages.plenty import get_data_from_plentymarkets
from facebook_feed_sync.packages.gsheet import GSHEET_HEADER
import facebook_feed_sync.packages.shared_data as shared


# =======================================================
# Sample data


@pytest.fixture
def sample_variations() -> list:
    """
        3 sample variations with a minimal response body with the options:
        ['properties', 'variationSalesPrices', 'images',
         'variationAttributeValues', 'stock']
    """
    sample = [
        {'id': 33,
         'images': [{'availabilities': [{'type': 'marketplace', 'value': 4}],
                     'url': 'https://test_image.com/image_1.jpg',
                     'position': 1}],
         'isActive': True,
         'isMain': False,
         'itemId': 1,
         'mainVariationId': 30,
         'mainWarehouseId': 1,
         'number': '1234x',
         'position': 1,
         'properties': [{'id': 12,
                         'propertyId': 2,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 2,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 33,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 12, 'lang': 'DE',
                              'value': 'https://test_link.com?num=1'}]},
                        {'id': 13,
                         'propertyId': 3,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 3,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 33,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 13, 'lang': 'DE',
                              'value': 'Baumwolle'},
                             {'id': 13, 'lang': 'EN',
                              'value': 'Cotton'}]}],
         'stock': [{'itemId': 1,
                    'netStock': 10,
                    'physicalStock': 12,
                    'variationId': 33,
                    'warehouseId': 1}],
         'variationAttributeValues': [{'attribute': {'backendName': 'color',
                                                     'id': 2,
                                                     'position': 2},
                                       'attributeId': 2,
                                       'attributeValue': {'attributeId': 2,
                                                          'backendName': 'red',
                                                          'id': 13,
                                                          'position': 1},
                                       'valueId': 13},
                                      {'attribute': {'backendName': 'size',
                                                     'id': 3,
                                                     'position': 3},
                                       'attributeId': 3,
                                       'attributeValue': {'attributeId': 3,
                                                          'backendName': 'M',
                                                          'id': 23,
                                                          'position': 1},
                                       'valueId': 23}],
         'variationSalesPrices': [{'price': 1.5,
                                   'salesPriceId': 1}],
         'weightG': 100},
        {'id': 44,
         'images': [{'availabilities': [{'type': 'marketplace', 'value': 4}],
                     'url': 'https://test_image.com/image_2.jpg',
                     'position': 1}],
         'isActive': True,
         'isMain': False,
         'itemId': 2,
         'mainVariationId': 40,
         'mainWarehouseId': 1,
         'number': '1345x',
         'position': 1,
         'properties': [{'id': 12,
                         'propertyId': 2,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 2,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 44,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 12, 'lang': 'DE',
                              'value': 'https://test_link.com?num=2'}]},
                        {'id': 13,
                         'propertyId': 3,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 3,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 44,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 13, 'lang': 'DE',
                              'value': 'Hanf'},
                             {'id': 13, 'lang': 'EN',
                              'value': 'Hemp'}]}],
         'stock': [{'itemId': 2,
                    'netStock': 11,
                    'physicalStock': 12,
                    'variationId': 44,
                    'warehouseId': 1}],
         'variationAttributeValues': [{'attribute': {'backendName': 'color',
                                                     'id': 2,
                                                     'position': 2},
                                       'attributeId': 2,
                                       'attributeValue': {'attributeId': 2,
                                                          'backendName':
                                                          'green',
                                                          'id': 14,
                                                          'position': 2},
                                       'valueId': 14},
                                      {'attribute': {'backendName': 'size',
                                                     'id': 3,
                                                     'position': 3},
                                       'attributeId': 3,
                                       'attributeValue': {'attributeId': 3,
                                                          'backendName': 'L',
                                                          'id': 24,
                                                          'position': 2},
                                       'valueId': 24}],
         'variationSalesPrices': [{'price': 1.6,
                                   'salesPriceId': 1}],
         'weightG': 100},
        {'id': 55,
         'images': [{'availabilities': [{'type': 'marketplace', 'value': 4}],
                     'url': 'https://test_image.com/image_3.jpg',
                     'position': 1}],
         'isActive': True,
         'isMain': False,
         'itemId': 3,
         'mainVariationId': 50,
         'mainWarehouseId': 1,
         'number': '1456x',
         'position': 1,
         'properties': [{'id': 12,
                         'propertyId': 2,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 2,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 55,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 12, 'lang': 'DE',
                              'value': 'https://test_link.com?num=3'}]},
                        {'id': 13,
                         'propertyId': 3,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 3,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 44,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 13, 'lang': 'DE',
                              'value': 'Baumwolle'},
                             {'id': 13, 'lang': 'EN',
                              'value': 'Cotton'}]}],
         'stock': [{'itemId': 3,
                    'netStock': 12,
                    'physicalStock': 12,
                    'variationId': 55,
                    'warehouseId': 2}],
         'variationAttributeValues': [{'attribute': {'backendName': 'color',
                                                     'id': 2,
                                                     'position': 2},
                                       'attributeId': 2,
                                       'attributeValue': {'attributeId': 2,
                                                          'backendName':
                                                          'blue',
                                                          'id': 15,
                                                          'position': 3},
                                       'valueId': 15},
                                      {'attribute': {'backendName': 'size',
                                                     'id': 3,
                                                     'position': 3},
                                       'attributeId': 3,
                                       'attributeValue': {'attributeId': 3,
                                                          'backendName': 'XL',
                                                          'id': 25,
                                                          'position': 3},
                                       'valueId': 25}],
         'variationSalesPrices': [{'price': 1.7,
                                   'salesPriceId': 1}],
         'weightG': 100},
        {'id': 66,
         'images': [{'availabilities': [{'type': 'marketplace', 'value': 5}],
                     'url': 'https://test_image.com/image_41.jpg',
                     'position': 2},
                    {'availabilities': [{'type': 'marketplace', 'value': 5}],
                     'url': 'https://test_image.com/image_4.jpg',
                     'position': 1}],
         'isActive': True,
         'isMain': False,
         'itemId': 4,
         'mainVariationId': 60,
         'mainWarehouseId': 1,
         'number': '1567x',
         'position': 1,
         'properties': [{'id': 12,
                         'propertyId': 2,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 2,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 66,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 12, 'lang': 'EN',
                              'value': 'https://test_link.com?num=4'}]},
                        {'id': 13,
                         'propertyId': 3,
                         'propertyRelation': {'cast': 'shortText',
                                              'id': 3,
                                              'typeIdentifier': 'item'},
                         'relationTargetId': 44,
                         'relationTypeIdentifier': 'item',
                         'relationValues': [
                             {'id': 13, 'lang': 'DE',
                              'value': 'Baumwolle'},
                             {'id': 13, 'lang': 'EN',
                              'value': 'Cotton'}]}],
         'stock': [{'itemId': 4,
                    'netStock': 0,
                    'physicalStock': 2,
                    'variationId': 66,
                    'warehouseId': 1}],
         'variationAttributeValues': [{'attribute': {'backendName': 'color',
                                                     'id': 2,
                                                     'position': 2},
                                       'attributeId': 2,
                                       'attributeValue': {'attributeId': 2,
                                                          'backendName':
                                                          'yellow',
                                                          'id': 16,
                                                          'position': 4},
                                       'valueId': 16}],
         'variationSalesPrices': [{'price': 1.8,
                                   'salesPriceId': 1}],
         'weightG': 100}
    ]
    return sample


# =======================================================
# Mock functions


@pytest.fixture
def mock_plenty_api_items_response_de() -> list:
    """ sample item with minimal response body and with 'itemProperties' """
    response = [
        {'flagOne': 18,
         'flagTwo': 0,
         'id': 1,
         'itemProperties': [
             {
                 'id': 10,
                 'itemId': 2,
                 'propertyId': 2,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Apparel & Accessories > Clothing > Pants',
                         'valueId': 10
                     },
                     {
                         'lang': 'en',
                         'value': 'Apparel & Accessories > Clothing > Pants',
                         'valueId': 10
                     }
                 ]
             },
             {
                 'id': 11,
                 'itemId': 1,
                 'propertyId': 3,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Herren',
                         'valueId': 11
                     },
                     {
                         'lang': 'en',
                         'value': 'Men',
                         'valueId': 11
                     }
                 ]
             },
             {
                 'id': 12,
                 'itemId': 1,
                 'propertyId': 4,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Erwachsener',
                         'valueId': 12
                     },
                     {
                         'lang': 'en',
                         'value': 'Adult',
                         'valueId': 12
                     }
                 ]
             }
         ],
         'itemType': 'default',
         'mainVariationId': '1230x',
         'manufacturerId': 3,
         'ownerId': None,
         'position': 0,
         'producingCountryId': 1,
         'texts': [{'description': '<p>test_beschreibung 1</p>',
                    'lang': 'de',
                    'name1': 'Testartikel',
                    'name2': 'Testartikel_2',
                    'name3': 'test_titel_1',
                    'urlPath': 'testartikel'}]},
        {'flagOne': 18,
         'flagTwo': 0,
         'id': 2,
         'itemProperties': [
             {
                 'id': 10,
                 'itemId': 2,
                 'propertyId': 2,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Apparel & Accessories > Clothing > Skirts',
                         'valueId': 10
                     },
                     {
                         'lang': 'en',
                         'value': 'Apparel & Accessories > Clothing > Skirts',
                         'valueId': 10
                     }
                 ]
             },
             {
                 'id': 11,
                 'itemId': 1,
                 'propertyId': 3,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Damen',
                         'valueId': 11
                     },
                     {
                         'lang': 'en',
                         'value': 'Women',
                         'valueId': 11
                     }
                 ]
             },
             {
                 'id': 12,
                 'itemId': 1,
                 'propertyId': 4,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Erwachsener',
                         'valueId': 12
                     },
                     {
                         'lang': 'en',
                         'value': 'Adult',
                         'valueId': 12
                     }
                 ]
             }
         ],
         'itemType': 'default',
         'mainVariationId': '1340x',
         'manufacturerId': 4,
         'ownerId': None,
         'position': 0,
         'producingCountryId': 1,
         'texts': [{'description': '<p>test_beschreibung 2</p>',
                    'lang': 'de',
                    'name1': 'Testartikel',
                    'name2': 'Testartikel_2',
                    'name3': 'test_titel_2',
                    'urlPath': 'testartikel'}]},
        {'flagOne': 18,
         'flagTwo': 0,
         'id': 3,
         'itemProperties': [
             {
                 'id': 10,
                 'itemId': 3,
                 'propertyId': 2,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Apparel & Accessories > Clothing > Suits',
                         'valueId': 10
                     },
                     {
                         'lang': 'en',
                         'value': 'Apparel & Accessories > Clothing > Suits',
                         'valueId': 10
                     }
                 ]
             },
             {
                 'id': 11,
                 'itemId': 3,
                 'propertyId': 3,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Herren',
                         'valueId': 11
                     },
                     {
                         'lang': 'en',
                         'value': 'Men',
                         'valueId': 11
                     }
                 ]
             },
             {
                 'id': 12,
                 'itemId': 3,
                 'propertyId': 4,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Erwachsener',
                         'valueId': 12
                     },
                     {
                         'lang': 'en',
                         'value': 'Adult',
                         'valueId': 12
                     }
                 ]
             }
         ],
         'itemType': 'default',
         'mainVariationId': '1450x',
         'manufacturerId': 5,
         'ownerId': None,
         'position': 0,
         'producingCountryId': 1,
         'texts': [{'description': '<p>test_beschreibung 3</p>',
                    'lang': 'de',
                    'name1': 'Testartikel',
                    'name2': 'Testartikel_2',
                    'name3': 'test_titel_3',
                    'urlPath': 'testartikel'}]},
        {'flagOne': 18,
         'flagTwo': 0,
         'id': 4,
         'itemProperties': [
             {
                 'id': 10,
                 'itemId': 4,
                 'propertyId': 2,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Apparel & Accessories > Clothing > Jackets',
                         'valueId': 10
                     },
                     {
                         'lang': 'en',
                         'value': 'Apparel & Accessories > Clothing > Jackets',
                         'valueId': 10
                     }
                 ]
             },
             {
                 'id': 11,
                 'itemId': 4,
                 'propertyId': 3,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Herren',
                         'valueId': 11
                     },
                     {
                         'lang': 'en',
                         'value': 'Men',
                         'valueId': 11
                     }
                 ]
             },
             {
                 'id': 12,
                 'itemId': 4,
                 'propertyId': 4,
                 'valueTexts': [
                     {
                         'lang': 'de',
                         'value': 'Erwachsener',
                         'valueId': 12
                     },
                     {
                         'lang': 'en',
                         'value': 'Adult',
                         'valueId': 12
                     }
                 ]
             }
         ],
         'itemType': 'default',
         'mainVariationId': '1560x',
         'manufacturerId': 3,
         'ownerId': None,
         'position': 0,
         'producingCountryId': 1,
         'texts': [{'description': '<p>test_beschreibung 4</p>',
                    'lang': 'de',
                    'name1': 'Testartikel',
                    'name2': 'Testartikel_2',
                    'name3': '',
                    'urlPath': 'testartikel'}]}
    ]
    return response


@pytest.fixture
def mock_plenty_api_items_response_en(
        mock_plenty_api_items_response_de) -> list:
    """ sample get items response body with values in english language """
    resp = mock_plenty_api_items_response_de
    for i in range(len(resp)):
        text = resp[i]['texts'][0]
        text['description'] = text['description'].replace(
            '_beschreibung', '_desc')
        text['lang'] = 'en'
        if text['name3']:
            text['name3'] = text['name3'].replace('titel', 'title')
    return resp


@pytest.fixture
def mock_plenty_api_attribute_response() -> list:
    response = [
        {
            'backendName': 'color',
            'id': 2,
            'position': 1,
            'values': [
                {
                    'attributeId': 2,
                    'backendName': 'red',
                    'id': 13,
                    'position': 1,
                    'valueNames': [{'lang': 'de',
                                    'name': 'rot',
                                    'valueId': '13'},
                                   {'lang': 'en',
                                    'name': 'red',
                                    'valueId': '13'}]
                },
                {
                    'attributeId': 2,
                    'backendName': 'green',
                    'id': 14,
                    'position': 2,
                    'valueNames': [{'lang': 'de',
                                    'name': 'grün',
                                    'valueId': '14'},
                                   {'lang': 'en',
                                    'name': 'green',
                                    'valueId': '14'}]
                },
                {
                    'attributeId': 2,
                    'backendName': 'blue',
                    'id': 15,
                    'position': 3,
                    'valueNames': [{'lang': 'de',
                                    'name': 'blau',
                                    'valueId': '15'},
                                   {'lang': 'en',
                                    'name': 'blue',
                                    'valueId': '15'}]
                },
                {
                    'attributeId': 2,
                    'backendName': 'yellow',
                    'id': 16,
                    'position': 4,
                    'valueNames': [{'lang': 'de',
                                    'name': 'gelb',
                                    'valueId': '16'},
                                   {'lang': 'en',
                                    'name': 'yellow',
                                    'valueId': '16'}]
                }
            ]
        },
        {
            'backendName': 'size',
            'id': 3,
            'position': 2,
            'values': [
                {
                    'attributeId': 3,
                    'backendName': 'M',
                    'id': 23,
                    'position': 1,
                    'valueNames': [{'lang': 'de',
                                    'name': 'M',
                                    'valueId': '23'},
                                   {'lang': 'en',
                                    'name': 'M',
                                    'valueId': '23'}]
                },
                {
                    'attributeId': 3,
                    'backendName': 'L',
                    'id': 24,
                    'position': 2,
                    'valueNames': [{'lang': 'de',
                                    'name': 'L',
                                    'valueId': '24'},
                                   {'lang': 'en',
                                    'name': 'L',
                                    'valueId': '24'}]
                },
                {
                    'attributeId': 3,
                    'backendName': 'XL',
                    'id': 25,
                    'position': 3,
                    'valueNames': [{'lang': 'de',
                                    'name': 'XL',
                                    'valueId': '25'},
                                   {'lang': 'en',
                                    'name': 'XL',
                                    'valueId': '25'}]
                }
            ]
        }
    ]
    return response


@pytest.fixture
def mock_plenty_api_manufacturers_response() -> list:
    response = [
        {
            'id': 3,
            'name': 'Test_company_1',
            'position': 1
        },
        {
            'id': 4,
            'name': 'Test_company_2',
            'position': 2
        },
        {
            'id': 5,
            'name': 'Test_company_3',
            'position': 3
        }
    ]
    return response


# =======================================================
# EXPECTED DATA


@pytest.fixture
def expected_get_data_from_pm() -> dict:
    llist = [
        ['1234x', '10'],
        ['1345x', '11'],
        ['1456x', '0'],
        ['1567x', '0']
    ]
    inventory = pandas.DataFrame(llist, columns=['id', 'inventory'], dtype=str)

    llist = [
        ['1234x', '1,50 EUR'],
        ['1345x', '1,60 EUR'],
        ['1456x', '1,70 EUR'],
        ['1567x', '1,80 EUR']
    ]
    price = pandas.DataFrame(llist, columns=['id', 'price'], dtype=str)

    llist = [
        ['1234x', 'test_titel_1', '<p>test_beschreibung 1</p>'],
        ['1345x', 'test_titel_2', '<p>test_beschreibung 2</p>'],
        ['1456x', 'test_titel_3', '<p>test_beschreibung 3</p>'],
        ['1567x', '', '<p>test_beschreibung 4</p>']
    ]
    text_de = pandas.DataFrame(llist, columns=['id', 'title', 'description'],
                               dtype=str)

    llist = [
        ['1234x', 'test_title_1', '<p>test_desc 1</p>'],
        ['1345x', 'test_title_2', '<p>test_desc 2</p>'],
        ['1456x', 'test_title_3', '<p>test_desc 3</p>'],
        ['1567x', '', '<p>test_desc 4</p>']
    ]
    text_en = pandas.DataFrame(llist, columns=['id', 'title', 'description'],
                               dtype=str)

    llist = [
        ['1234x', '', ''],
        ['1345x', '', ''],
        ['1456x', '', ''],
        ['1567x', '', '']
    ]
    text_it = pandas.DataFrame(llist, columns=['id', 'title', 'description'],
                               dtype=str)

    llist = [
        ['1234x', 'rot', 'M'],
        ['1345x', 'grün', 'L'],
        ['1456x', 'blau', 'XL'],
        ['1567x', 'gelb', '']
    ]
    attribute_de = pandas.DataFrame(llist, columns=['id', 'color', 'size'],
                                    dtype=str)

    llist = [
        ['1234x', 'red', 'M'],
        ['1345x', 'green', 'L'],
        ['1456x', 'blue', 'XL'],
        ['1567x', 'yellow', '']
    ]
    attribute_en = pandas.DataFrame(llist, columns=['id', 'color', 'size'],
                                    dtype=str)

    llist = [
        ['1234x', '', ''],
        ['1345x', '', ''],
        ['1456x', '', ''],
        ['1567x', '', '']
    ]
    attribute_it = pandas.DataFrame(llist, columns=['id', 'color', 'size'],
                                    dtype=str)

    llist = [
        ['1234x', 'https://test_link.com?num=1',
         'https://test_image.com/image_1.jpg'],
        ['1345x', 'https://test_link.com?num=2',
         'https://test_image.com/image_2.jpg'],
        ['1456x', 'https://test_link.com?num=3',
         'https://test_image.com/image_3.jpg'],
        ['1567x', 'https://test_link.com?num=4',
         '']
    ]
    link = pandas.DataFrame(llist, columns=['id', 'link', 'image_link'],
                            dtype=str)

    llist = [
        [
            '1234x', 'test_titel_1', '<p>test_beschreibung 1</p>', 'in stock',
            '10', 'new', '1,50 EUR', 'https://test_link.com?num=1',
            'https://test_image.com/image_1.jpg', 'Test_company_1',
            'Apparel & Accessories > Clothing > Pants', '', '', '1',
            'Herren', 'rot', 'M', 'Adult', 'Baumwolle', '', '', '', '100 g'
        ]
    ]
    single = pandas.DataFrame(llist, columns=GSHEET_HEADER, dtype=str)

    llist = [
        [
            '1234x', 'test_title_1', '<p>test_desc 1</p>', 'in stock',
            '10', 'new', '1,50 EUR', 'https://test_link.com?num=1',
            'https://test_image.com/image_1.jpg', 'Test_company_1',
            'Apparel & Accessories > Clothing > Pants', '', '', '1',
            'Men', 'red', 'M', 'Adult', 'Cotton', '', '', '', '100 g'
        ]
    ]
    single_en = pandas.DataFrame(llist, columns=GSHEET_HEADER, dtype=str)

    llist = [
        [
            '1234x', 'test_titel_1', '<p>test_beschreibung 1</p>', 'in stock',
            '10', 'new', '1,50 EUR', 'https://test_link.com?num=1',
            'https://test_image.com/image_1.jpg', 'Test_company_1',
            'Apparel & Accessories > Clothing > Pants', '', '', '1',
            'Herren', 'rot', 'M', 'Adult', 'Baumwolle', '', '', '', '100 g'
        ],
        [
            '1345x', 'test_titel_2', '<p>test_beschreibung 2</p>', 'in stock',
            '11', 'new', '1,60 EUR', 'https://test_link.com?num=2',
            'https://test_image.com/image_2.jpg', 'Test_company_2',
            'Apparel & Accessories > Clothing > Skirts', '', '', '2',
            'Damen', 'grün', 'L', 'Adult', 'Hanf', '', '', '', '100 g'
        ],
        [
            '1456x', 'test_titel_3', '<p>test_beschreibung 3</p>',
            'out of stock', '0', 'new', '1,70 EUR',
            'https://test_link.com?num=3',
            'https://test_image.com/image_3.jpg', 'Test_company_3',
            'Apparel & Accessories > Clothing > Suits', '', '', '3',
            'Herren', 'blau', 'XL', 'Adult', 'Baumwolle', '', '', '', '100 g'
        ]
    ]
    multi = pandas.DataFrame(llist, columns=GSHEET_HEADER, dtype=str)

    expect = {
        'inventory': inventory, 'price': price,
        'text': {'de': text_de, 'en': text_en, 'it': text_it},
        'attribute': {'de': attribute_de, 'en': attribute_en,
                      'it': attribute_it},
        'link': link, 'no_variation': pandas.DataFrame(),
        'single': {'de': single, 'en': single_en},
        'multi': multi, 'api_error': pandas.DataFrame()
              }

    return expect


# =======================================================
# Unit tests


def describe_get_data_from_plentymarkets() -> None:
    def with_sync_type_inventory(sample_variations: list,
                                 expected_get_data_from_pm: dict):
        shared.plenty_variations = sample_variations
        shared.warehouse_id = 1
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'inventory']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(expected_get_data_from_pm['inventory'],
                           result)

    def with_sync_type_price(sample_variations: list,
                             expected_get_data_from_pm: dict):
        shared.plenty_variations = sample_variations
        shared.price_id = 1
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'price']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(expected_get_data_from_pm['price'],
                           result)

    def with_sync_type_text(sample_variations: list,
                            expected_get_data_from_pm: dict,
                            mock_plenty_api_items_response_de: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.item_name_number = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_de
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'title', 'description']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(expected_get_data_from_pm['text']['de'],
                           result)

    def with_sync_type_text_en(sample_variations: list,
                               expected_get_data_from_pm: dict,
                               mock_plenty_api_items_response_en: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'en'
        shared.item_name_number = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_en
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'title', 'description']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(expected_get_data_from_pm['text']['en'],
                           result)

    def with_sync_type_text_it(sample_variations: list,
                               expected_get_data_from_pm: dict,
                               mock_plenty_api_items_response_en: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'it'
        shared.item_name_number = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_en
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'title', 'description']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(expected_get_data_from_pm['text']['it'],
                           result)

    def with_sync_type_attribute(sample_variations: list,
                                 expected_get_data_from_pm: dict,
                                 mock_plenty_api_attribute_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.color_attribute_id = 2
        shared.size_attribute_id = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'color', 'size']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(
            expected_get_data_from_pm['attribute']['de'], result)

    def with_sync_type_attribute_en(sample_variations: list,
                                    expected_get_data_from_pm: dict,
                                    mock_plenty_api_attribute_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'en'
        shared.color_attribute_id = 2
        shared.size_attribute_id = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'color', 'size']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(
            expected_get_data_from_pm['attribute']['en'], result)

    def with_sync_type_attribute_it(sample_variations: list,
                                    expected_get_data_from_pm: dict,
                                    mock_plenty_api_attribute_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'it'
        shared.color_attribute_id = 2
        shared.size_attribute_id = 3
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'color', 'size']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(
            expected_get_data_from_pm['attribute']['it'], result)

    def with_sync_type_link(sample_variations: list,
                            expected_get_data_from_pm: dict):
        shared.plenty_variations = sample_variations
        shared.url_property_id = 2
        shared.referrer = 4
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'link', 'image_link']

        result = get_data_from_plentymarkets(header=header)

        assert_frame_equal(
            expected_get_data_from_pm['link'], result)

    def with_invalid_sync_type(sample_variations: list,
                               expected_get_data_from_pm: dict):
        shared.plenty_variations = sample_variations
        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        shared.plenty_api_instance = mock_plenty
        header = ['id', 'invalid']

        result = get_data_from_plentymarkets(header=header)

        assert len(result.index) == 0

    def with_no_variation(sample_variations: list,
                          expected_get_data_from_pm: dict,
                          mock_plenty_api_items_response_de: list,
                          mock_plenty_api_attribute_response: list,
                          mock_plenty_api_manufacturers_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.item_name_number = 3
        shared.gender_property_id = 3
        shared.age_property_id = 4
        shared.google_category_property_id = 2
        shared.url_property_id = 2
        shared.material_property_id = 3

        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_de
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        mock_plenty.plenty_api_get_manufacturers.return_value =\
            mock_plenty_api_manufacturers_response
        shared.plenty_api_instance = mock_plenty
        target = []

        result = get_data_from_plentymarkets(target=target)

        assert_frame_equal(expected_get_data_from_pm['no_variation'],
                           result)

    def with_one_variation(sample_variations: list,
                           expected_get_data_from_pm: dict,
                           mock_plenty_api_items_response_de: list,
                           mock_plenty_api_attribute_response: list,
                           mock_plenty_api_manufacturers_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.item_name_number = 3
        shared.gender_property_id = 3
        shared.age_property_id = 4
        shared.google_category_property_id = 2
        shared.url_property_id = 2
        shared.material_property_id = 3

        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_de
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        mock_plenty.plenty_api_get_manufacturers.return_value =\
            mock_plenty_api_manufacturers_response
        shared.plenty_api_instance = mock_plenty
        target = ['1234x']

        result = get_data_from_plentymarkets(target=target)

        assert_frame_equal(expected_get_data_from_pm['single']['de'],
                           result)

    def with_one_variation_en(sample_variations: list,
                              expected_get_data_from_pm: dict,
                              mock_plenty_api_items_response_en: list,
                              mock_plenty_api_attribute_response: list,
                              mock_plenty_api_manufacturers_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'en'
        shared.item_name_number = 3
        shared.gender_property_id = 3
        shared.age_property_id = 4
        shared.google_category_property_id = 2
        shared.url_property_id = 2
        shared.material_property_id = 3

        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_en
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        mock_plenty.plenty_api_get_manufacturers.return_value =\
            mock_plenty_api_manufacturers_response
        shared.plenty_api_instance = mock_plenty
        target = ['1234x']

        result = get_data_from_plentymarkets(target=target)

        assert_frame_equal(expected_get_data_from_pm['single']['en'],
                           result)

    def with_multiple_variations(sample_variations: list,
                                 expected_get_data_from_pm: dict,
                                 mock_plenty_api_items_response_de: list,
                                 mock_plenty_api_attribute_response: list,
                                 mock_plenty_api_manufacturers_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.item_name_number = 3
        shared.gender_property_id = 3
        shared.age_property_id = 4
        shared.google_category_property_id = 2
        shared.url_property_id = 2
        shared.material_property_id = 3

        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value =\
            mock_plenty_api_items_response_de
        mock_plenty.plenty_api_get_attributes.return_value =\
            mock_plenty_api_attribute_response
        mock_plenty.plenty_api_get_manufacturers.return_value =\
            mock_plenty_api_manufacturers_response
        shared.plenty_api_instance = mock_plenty
        target = ['1234x', '1345x', '1456x']

        result = get_data_from_plentymarkets(target=target)

        assert_frame_equal(expected_get_data_from_pm['multi'],
                           result)

    def with_api_error(sample_variations: list,
                       expected_get_data_from_pm: dict,
                       mock_plenty_api_items_response_de: list,
                       mock_plenty_api_attribute_response: list,
                       mock_plenty_api_manufacturers_response: list):
        shared.plenty_variations = sample_variations
        shared.lang = 'de'
        shared.gender_property_id = 3
        shared.age_property_id = 4
        shared.google_category_property_id = 2
        shared.url_property_id = 2
        shared.material_property_id = 3

        mock_plenty = unittest.mock.Mock(spec=plenty_api.PlentyApi)
        mock_plenty.plenty_api_get_items.return_value = []
        mock_plenty.plenty_api_get_attributes.return_value = []
        mock_plenty.plenty_api_get_manufacturers.return_value = []
        shared.plenty_api_instance = mock_plenty
        target = ['1234x']

        result = get_data_from_plentymarkets(target=target)

        assert_frame_equal(expected_get_data_from_pm['api_error'],
                           result)
