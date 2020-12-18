import pandas
import pytest
import inspect

from pandas.testing import assert_frame_equal

from packages.stock_compare import export_header_check, detect_differences

@pytest.fixture
def example_correct_dataframe():
    columns = ['Variation.number', 'VariationStock.physicalStock.Warehouse']
    data = [['L12',10], ['K13', 15]]
    return pandas.DataFrame(data, columns=columns)

@pytest.fixture
def example_bad_dataframe_wrong_header():
    columns = ['Sku', 'Stock']
    data = [['L12',10], ['K13', 15]]
    return pandas.DataFrame(data, columns=columns)

@pytest.fixture
def stock_frame_target():
    data = [['1234x', 10], ['2345x', 12], ['3456x', 15], ['4567x', 20]]
    return pandas.DataFrame(data, columns=['Sku', 'FB_inventory'])

@pytest.fixture
def stock_frame_source():
    data = [['1234x', 10], ['2345x', 30], ['3456x', 5], ['4567x', 0]]
    return pandas.DataFrame(data, columns=['Sku', 'Plenty_inventory'])

def test_export_header_check_OK(example_correct_dataframe):
    result = export_header_check(
        frame=example_correct_dataframe, sku_column='Variation.number',
        stock_column='VariationStock.physicalStock.Warehouse')

    assert result is True

def test_export_header_check_BAD_header(example_bad_dataframe_wrong_header):
    result = export_header_check(
        frame=example_bad_dataframe_wrong_header,
        sku_column='Variation.number',
        stock_column='VariationStock.physicalStock.Warehouse')

    assert result is False

def test_export_header_check_WRONG_warehouse(example_correct_dataframe):
    result = export_header_check(
        frame=example_correct_dataframe, sku_column='Variation.number',
        stock_column='VariationStock.physicalStock.Bad')

    assert result is False

def test_detect_differences(stock_frame_target, stock_frame_source):
    result = detect_differences(google=stock_frame_target,
                                plenty=stock_frame_source)
    expect = pandas.DataFrame([['2345x', 12, 30], ['3456x', 15, 5],
                               ['4567x', 20, 0]],
                              columns=['Sku', 'FB_inventory',
                                       'Plenty_inventory'], index=[1,2,3])

    assert_frame_equal(result, expect)
