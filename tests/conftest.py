import pytest
from pathlib import Path
import pandas as pd
import json
from beeromancy_back.data_processers import ScrapedDataProcesser

@pytest.fixture(scope="session")
def test_raw_data():
    path = Path(__file__).parent / "test_data"/"test_products_data.json"
    processer = ScrapedDataProcesser()
    with open(path, 'r', encoding='utf-8') as f:
        return processer.get_cleared_data(f)