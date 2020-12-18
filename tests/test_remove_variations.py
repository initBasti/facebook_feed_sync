import pytest
import pandas

@pytest.fixture
def sample_google_sheet():
    sample = pandas.DataFrame(
        [
            ['1234x', 'variation-1', 'description', 'in stock', 18],
            ['1235x', 'variation-2', 'description', 'in stock', 8],
            ['1236x', 'variation-3', 'description', 'in stock', 22],
            ['1237x', 'variation-4', 'description', 'in stock', 1],
            ['1238x', 'variation-5', 'description', 'in stock', 4],
            ['1239x', 'variation-6', 'description', 'in stock', 9]
        ], columns=['id', 'title', 'description', 'availability', 'inventory']
    )
    return sample

@pytest.fixture
def sample_plenty_export():
    sample = pandas.DataFrame(
        []
    )
