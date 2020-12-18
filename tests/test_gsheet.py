import pytest
from pytest_mock import mocker
import pandas
from pandas.testing import assert_frame_equal

from facebook_feed_sync.packages.gsheet import (
    add_new_items, delete_removed_items, update_column, GSHEET_HEADER
)


get_data_function =\
    'facebook_feed_sync.packages.plenty.get_data_from_plentymarkets'


@pytest.fixture
def google_items() -> list:
    llist = [
        ['1234', 'Test name 1', 'test_description_1', 'in stock', '15',
         'new', '25,7 EUR', 'https://test_link.com?number=1234',
         'https://test_image.com/image_1234.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'black', 'M', 'adult', 'cotton', '', '', '', '157 g'],
        ['1235', 'Test name 2', 'test_description_2', 'in stock', '18',
         'new', '25,7 EUR', 'https://test_link.com?number=1235',
         'https://test_image.com/image_1235.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'black', 'L', 'adult', 'cotton', '', '', '', '157 g'],
        ['1236', 'Test name 3', 'test_description_3', 'in stock', '22',
         'new', '25,7 EUR', 'https://test_link.com?number=1236',
         'https://test_image.com/image_1236.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'black', 'XL', 'adult', 'cotton', '', '', '', '157 g'],
        ['1237', 'Test name 4', 'test_description_4', 'in stock', '23',
         'new', '25,7 EUR', 'https://test_link.com?number=1237',
         'https://test_image.com/image_1237.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'grey', 'M', 'adult', 'cotton', '', '', '', '157 g'],
        ['1238', 'Test name 5', 'test_description_5', 'in stock', '25',
         'new', '25,7 EUR', 'https://test_link.com?number=1238',
         'https://test_image.com/image_1238.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'grey', 'L', 'adult', 'cotton', '', '', '', '157 g'],
        ['1239', 'Test name 6', 'test_description_6', 'in stock', '27',
         'new', '25,7 EUR', 'https://test_link.com?number=1239',
         'https://test_image.com/image_1239.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'grey', 'XL', 'adult', 'cotton', '', '', '', '157 g'],
        ['1345', 'Test pants 1', 'test_description_7', 'in stock', '21',
         'new', '18,7 EUR', 'https://test_link.com?number=1345',
         'https://test_image.com/image_1345.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Pants', '', '', '1340',
         'male', 'olive-green', 'M', 'adult', 'cotton', '', '', '', '157 g'],
        ['1346', 'Test pants 2', 'test_description_8', 'in stock', '11',
         'new', '25,7 EUR', 'https://test_link.com?number=1346',
         'https://test_image.com/image_1346.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Pants', '', '', '1340',
         'male', 'olive-green', 'L', 'adult', 'cotton', '', '', '', '157 g'],
        ['1347', 'Test pants 3', 'test_description_9', 'in stock', '20',
         'new', '25,7 EUR', 'https://test_link.com?number=1347',
         'https://test_image.com/image_1347.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Pants', '', '', '1340',
         'male', 'blue', 'M', 'adult', 'cotton', '', '', '', '157 g'],
        ['1348', 'Test pants 4', 'test_description_10', 'in stock', '30',
         'new', '25,7 EUR', 'https://test_link.com?number=1348',
         'https://test_image.com/image_1348.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Pants', '', '', '1340',
         'male', 'blue', 'L', 'adult', 'cotton', '', '', '', '157 g']
    ]
    return llist


@pytest.fixture
def plenty_data() -> list:
    llist = [
        ['1240', 'Test name 7', 'test_description_7', 'in stock', '49',
         'new', '25,7 EUR', 'https://test_link.com?number=1240',
         'https://test_image.com/image_1240.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Shirts & Tops', '', '', '1230',
         'male', 'yellow', 'M', 'adult', 'cotton', '', '', '', '157 g'],
        ['1456', 'Test skirt 1', 'test_description_1', 'in stock', '45',
         'new', '35,7 EUR', 'https://test_link.com?number=1456',
         'https://test_image.com/image_1456.jpg', 'Test-company',
         'Apparel & Accessories > Clothing > Skirts', '', '', '1450',
         'male', 'pink', 'M', 'adult', 'cotton', '', '', '', '157 g']
    ]
    return llist


@pytest.fixture
def sample_google_sheet_normal(google_items) -> pandas.DataFrame:
    """ All rows contain all required values """
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def sample_google_sheet_with_missing_data(google_items) -> pandas.DataFrame:
    """ Some rows are missing a few values """
    # missing description
    google_items[0][2] = ''
    # missing name
    google_items[1][1] = ''
    # missing inventory
    google_items[2][4] = ''
    # missing price
    google_items[3][6] = ''
    # missing website link
    google_items[4][7] = ''
    # missing image link
    google_items[5][8] = ''
    # missing google category
    google_items[6][10] = ''
    # missing attributes
    google_items[7][15] = ''
    google_items[7][16] = ''
    google_items[7][18] = ''
    # missing shiping weight
    google_items[8][-1] = ''
    # missing parent id
    google_items[9][13] = ''
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def sample_plenty_data_new_items() -> pandas.DataFrame:
    llist = [
        ['1234', '10'],
        ['1235', '11'],
        ['1236', '12'],
        ['1237', '13'],
        ['1238', '14'],
        ['1239', '15'],
        ['1240', '20'],
        ['1345', '16'],
        ['1346', '17'],
        ['1347', '18'],
        ['1348', '19'],
        ['1456', '21']
    ]
    return pandas.DataFrame(llist, columns=['id', 'inventory'], dtype=str)


@pytest.fixture
def sample_plenty_data_less_items() -> pandas.DataFrame:
    # 1239 & 1348 missing
    llist = [
        ['1234', '10'],
        ['1235', '11'],
        ['1236', '12'],
        ['1237', '13'],
        ['1238', '14'],
        ['1345', '16'],
        ['1346', '17'],
        ['1347', '18']
    ]
    return pandas.DataFrame(llist, columns=['id', 'inventory'], dtype=str)


@pytest.fixture
def sample_plenty_data_inventory() -> pandas.DataFrame:
    llist = [
        ['1234', '10'],
        ['1235', '11'],
        ['1236', '12'],
        ['1237', '13'],
        ['1238', '14'],
        ['1239', '15'],
        ['1345', '16'],
        ['1346', '17'],
        ['1347', '18'],
        ['1348', '19']
    ]
    return pandas.DataFrame(llist, columns=['id', 'inventory'], dtype=str)


@pytest.fixture
def sample_plenty_data_price() -> pandas.DataFrame:
    llist = [
        ['1234', '10,5 EUR'],
        ['1235', '11,5 EUR'],
        ['1236', '12,5 EUR'],
        ['1237', '13,5 EUR'],
        ['1238', '14,5 EUR'],
        ['1239', '15,5 EUR'],
        ['1345', '16,5 EUR'],
        ['1346', '17,5 EUR'],
        ['1347', '18,5 EUR'],
        ['1348', '19,5 EUR']
    ]
    return pandas.DataFrame(llist, columns=['id', 'price'], dtype=str)


@pytest.fixture
def sample_plenty_data_texts() -> pandas.DataFrame:
    llist = [
        ['1234', 'Updated_title_1', 'Updated_description_1'],
        ['1235', 'Updated_title_2', 'Updated_description_2'],
        ['1236', 'Updated_title_3', 'Updated_description_3'],
        ['1237', 'Updated_title_4', 'Updated_description_4'],
        ['1238', 'Updated_title_5', 'Updated_description_5'],
        ['1239', 'Updated_title_6', 'Updated_description_6'],
        ['1345', 'Updated_title_7', 'Updated_description_7'],
        ['1346', 'Updated_title_8', 'Updated_description_8'],
        ['1347', 'Updated_title_9', 'Updated_description_9'],
        ['1348', 'Updated_title_10', 'Updated_description_10']
    ]
    return pandas.DataFrame(llist, columns=['id', 'title', 'description'],
                            dtype=str)


@pytest.fixture
def sample_plenty_data_attributes() -> pandas.DataFrame:
    llist = [
        ['1234', 'Updated_color_1', 'Updated_size_1'],
        ['1235', 'Updated_color_2', 'Updated_size_2'],
        ['1236', 'Updated_color_3', 'Updated_size_3'],
        ['1237', 'Updated_color_4', 'Updated_size_4'],
        ['1238', 'Updated_color_5', 'Updated_size_5'],
        ['1239', 'Updated_color_6', 'Updated_size_6'],
        ['1345', 'Updated_color_7', 'Updated_size_7'],
        ['1346', 'Updated_color_8', 'Updated_size_8'],
        ['1347', 'Updated_color_9', 'Updated_size_9'],
        ['1348', 'Updated_color_10', 'Updated_size_10']
    ]
    return pandas.DataFrame(llist, columns=['id', 'color', 'size'],
                            dtype=str)


@pytest.fixture
def sample_plenty_data_invalid() -> pandas.DataFrame:
    llist = [
        ['1234', '10'],
        ['1235', '11'],
        ['1236', '12'],
        ['1237', '13'],
        ['1238', '14'],
        ['1239', '15'],
        ['1345', '16'],
        ['1346', '17'],
        ['1347', '18'],
        ['1348', '19']
    ]
    return pandas.DataFrame(llist, columns=['id', 'invalid'], dtype=str)


@pytest.fixture
def sample_plenty_data_full(plenty_data) -> pandas.DataFrame:
    """ Return all required data from plentymarkets for a set of variations """
    return pandas.DataFrame(plenty_data, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def sample_plenty_data_partial(plenty_data) -> pandas.DataFrame:
    """ Return partial data from plentymarkets for a set of variations """
    # missing links
    plenty_data[0][7] = ''
    plenty_data[0][8] = ''
    # missing texts
    plenty_data[1][2] = ''
    return pandas.DataFrame(plenty_data, columns=GSHEET_HEADER, dtype=str)


# =======================================================
# EXPECTED ADD_NEW_ITEMS
@pytest.fixture
def expected_add_new_items_full(google_items, plenty_data):
    """ for add_new_items -> with_full_data """
    return pandas.DataFrame(google_items + plenty_data, columns=GSHEET_HEADER,
                            dtype=str)


@pytest.fixture
def expected_add_new_items_partial(google_items, plenty_data):
    """ for add_new_items -> with_partial_data """
    # missing links
    plenty_data[0][7] = ''
    plenty_data[0][8] = ''
    # missing texts
    plenty_data[1][2] = ''
    return pandas.DataFrame(google_items + plenty_data, columns=GSHEET_HEADER,
                            dtype=str)


# EXPECTED DELETE_REMOVED_ITEMS
@pytest.fixture
def expected_delete_removed_items_less_ids(google_items):
    """ for delete_removed_items -> with_less_ids """
    # remove 1239
    del google_items[5]
    # remove 1348 (index 8 because the size got reduced by 1)
    del google_items[8]
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


# EXPECTED UPDATE_COLUMN
@pytest.fixture
def expected_update_column_inventory(google_items):
    """ for update_column -> with_inventory """
    new_inv = 10
    for index, item in enumerate(google_items):
        item[4] = new_inv + index
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def expected_update_column_price(google_items):
    """ for update_column -> with_price """
    new_price = ['10,5 EUR', '11,5 EUR', '12,5 EUR', '13,5 EUR', '14,5 EUR',
                 '15,5 EUR', '16,5 EUR', '17,5 EUR', '18,5 EUR', '19,5 EUR']
    for index, item in enumerate(google_items):
        item[6] = new_price[index]
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def expected_update_column_texts(google_items):
    """ for update_column -> with_texts """
    new_titles = [
        'Updated_title_1', 'Updated_title_2', 'Updated_title_3',
        'Updated_title_4', 'Updated_title_5', 'Updated_title_6',
        'Updated_title_7', 'Updated_title_8', 'Updated_title_9',
        'Updated_title_10'
    ]
    new_desc = [
        'Updated_description_1', 'Updated_description_2',
        'Updated_description_3', 'Updated_description_4',
        'Updated_description_5', 'Updated_description_6',
        'Updated_description_7', 'Updated_description_8',
        'Updated_description_9', 'Updated_description_10'
    ]
    for index, item in enumerate(google_items):
        item[1] = new_titles[index]
        item[2] = new_desc[index]
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


@pytest.fixture
def expected_update_column_attributes(google_items):
    """ for update_column -> with_attributes """
    new_color = [
        'Updated_color_1', 'Updated_color_2', 'Updated_color_3',
        'Updated_color_4', 'Updated_color_5', 'Updated_color_6',
        'Updated_color_7', 'Updated_color_8', 'Updated_color_9',
        'Updated_color_10'
    ]
    new_size = [
        'Updated_size_1', 'Updated_size_2',
        'Updated_size_3', 'Updated_size_4',
        'Updated_size_5', 'Updated_size_6',
        'Updated_size_7', 'Updated_size_8',
        'Updated_size_9', 'Updated_size_10'
    ]
    for index, item in enumerate(google_items):
        item[15] = new_color[index]
        item[16] = new_size[index]
    return pandas.DataFrame(google_items, columns=GSHEET_HEADER, dtype=str)


# =======================================================


def describe_add_new_items():
    def with_equal_ids(sample_google_sheet_normal,
                       sample_plenty_data_full,
                       sample_plenty_data_inventory,
                       mocker):
        """
            Mock the get_full_data_from_plentymarkets function with
            the sample_plenty_data_full fixture.
        """
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_full
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_inventory)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_less_ids(sample_google_sheet_normal,
                      sample_plenty_data_full,
                      sample_plenty_data_less_items,
                      mocker):
        """
            Mock the get_full_data_from_plentymarkets function with
            the sample_plenty_data_full fixture.
        """
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_full
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_less_items)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_new_ids(sample_google_sheet_normal,
                     sample_plenty_data_full,
                     sample_plenty_data_new_items,
                     expected_add_new_items_full,
                     mocker):
        """
            Mock the get_full_data_from_plentymarkets function with
            the sample_plenty_data_full fixture.
        """
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_full
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_new_items)

        assert_frame_equal(expected_add_new_items_full, result)

    def with_malfunctioning_plenty_api(sample_google_sheet_normal,
                                       sample_plenty_data_inventory,
                                       mocker):
        """
            Mock the get_full_data_from_plentymarkets function with
            an empty dataframe result.
        """
        mocker.patch(
            get_data_function, return_value=pandas.DataFrame()
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_inventory)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_partial_data(sample_google_sheet_normal,
                          sample_plenty_data_partial,
                          sample_plenty_data_new_items,
                          expected_add_new_items_partial,
                          mocker):
        """
            Mock the get_full_data_from_plentymarkets function with
            the sample_plenty_data_partial fixture.
        """
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_partial
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_new_items)

        assert_frame_equal(expected_add_new_items_partial, result)

    def with_empty_google_sheet(sample_plenty_data_full,
                                sample_plenty_data_inventory,
                                mocker):
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_full
        )
        result = add_new_items(google=pandas.DataFrame(),
                               plenty=sample_plenty_data_inventory)

        # should be empty
        assert_frame_equal(pandas.DataFrame(), result)

    def with_empty_plenty_data(sample_google_sheet_normal,
                               sample_plenty_data_full,
                               mocker):
        mocker.patch(
            get_data_function, return_value=sample_plenty_data_full
        )
        result = add_new_items(google=sample_google_sheet_normal,
                               plenty=pandas.DataFrame())

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)


def describe_delete_removed_items():
    def with_equal_ids(sample_google_sheet_normal,
                       sample_plenty_data_inventory):
        result = delete_removed_items(google=sample_google_sheet_normal,
                                      plenty=sample_plenty_data_inventory)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_less_ids(sample_google_sheet_normal,
                      sample_plenty_data_less_items,
                      expected_delete_removed_items_less_ids):
        result = delete_removed_items(google=sample_google_sheet_normal,
                                      plenty=sample_plenty_data_less_items)

        assert_frame_equal(expected_delete_removed_items_less_ids, result)

    def with_new_ids(sample_google_sheet_normal,
                     sample_plenty_data_new_items):
        result = delete_removed_items(google=sample_google_sheet_normal,
                                      plenty=sample_plenty_data_new_items)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_empty_google_sheet(sample_plenty_data_inventory):
        result = delete_removed_items(google=pandas.DataFrame(),
                                      plenty=sample_plenty_data_inventory)

        # should be empty
        assert_frame_equal(pandas.DataFrame(), result)

    def with_empty_plenty_data(sample_google_sheet_normal):
        result = delete_removed_items(google=sample_google_sheet_normal,
                                      plenty=pandas.DataFrame())

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)


def describe_update_column():
    """
        update column should always follow a check for new or removed items
        but should signal if that is not the case
    """
    def with_less_ids(sample_google_sheet_normal,
                      sample_plenty_data_less_items):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_less_items)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_new_ids(sample_google_sheet_normal,
                     sample_plenty_data_new_items):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_new_items)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_inventory(sample_google_sheet_normal,
                       sample_plenty_data_inventory,
                       expected_update_column_inventory):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_inventory)

        assert_frame_equal(expected_update_column_inventory, result)

    def with_price(sample_google_sheet_normal,
                   sample_plenty_data_price,
                   expected_update_column_price):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_price)

        assert_frame_equal(expected_update_column_price, result)

    def with_texts(sample_google_sheet_normal,
                   sample_plenty_data_texts,
                   expected_update_column_texts):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_texts)

        assert_frame_equal(expected_update_column_texts, result)

    def with_attributes(sample_google_sheet_normal,
                        sample_plenty_data_attributes,
                        expected_update_column_attributes):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_attributes)

        assert_frame_equal(expected_update_column_attributes, result)

    def with_invalid_column(sample_google_sheet_normal,
                            sample_plenty_data_invalid):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=sample_plenty_data_invalid)

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)

    def with_empty_google_sheet(sample_plenty_data_inventory):
        result = update_column(google=pandas.DataFrame(),
                               plenty=sample_plenty_data_inventory)

        # should be empty
        assert_frame_equal(pandas.DataFrame(), result)

    def with_empty_plenty_data(sample_google_sheet_normal):
        result = update_column(google=sample_google_sheet_normal,
                               plenty=pandas.DataFrame())

        # should be unchanged
        assert_frame_equal(sample_google_sheet_normal, result)
