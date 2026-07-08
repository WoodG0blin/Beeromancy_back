import pytest
from pathlib import Path
import pandas as pd
import json
from beeromancy_back.data_processers import ScrapedDataProcesser

@pytest.fixture
def test_raw_data(scope="session"):
    path = Path(__file__).parent / "test_data"/"test_products_data.json"
    processer = ScrapedDataProcesser()
    with open(path, 'r', encoding='utf-8') as f:
        # return pd.json_normalize(json.load(f))
        return processer.get_cleared_data(f)