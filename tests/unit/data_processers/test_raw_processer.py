import pytest
import pandas as pd
from beeromancy_back.data_processers import ScrapedDataProcesser


@pytest.mark.parametrize("column, first_value", [
    ("color", "4.6 ebc"),
    ("extract", "84.0 %"),
    ("protein", "10.0 %"),
    ("share", "100.0 %"),
    ("kolbach", None),
    ("diastatic", None)
])
def test_get_malts_characteristics(test_raw_data, column, first_value):
    processor = ScrapedDataProcesser()
    selected_data = processor.get_malts_characteristics(test_raw_data[test_raw_data['item_type'] == 'malt'].copy())
    assess_selected_data(selected_data, column, first_value)


@pytest.mark.parametrize("column, first_value", [
    ("alpha", "7.0-10.0 %"),
    ("beta", "5.0-6.5 %"),
    ("cohumulon", "31.0-35.0 %"),
    ("oils", "2.2")
])
def test_get_hops_characteristics(test_raw_data, column, first_value):
    processor = ScrapedDataProcesser()
    selected_data = processor.get_hops_characteristics(test_raw_data[test_raw_data['item_type'] == 'hop'].copy())
    assess_selected_data(selected_data, column, first_value)


@pytest.mark.parametrize("column, first_value", [
    ("attenuation", "73.0-83.0 %"),
    ("flocculation", "низкая"),
    ("fermentation_temperature", "18.0-26.0 °с"),
    ("alcohol_tolerance", "10.0 %"),
    ("diastatic", "отрицательно"),
    ("fenolic", "положительно")
])
def test_get_yeasts_characteristics(test_raw_data, column, first_value):
    processor = ScrapedDataProcesser()
    selected_data = processor.get_yeasts_characteristics(test_raw_data[test_raw_data['item_type'] == 'yeast'].copy())
    assess_selected_data(selected_data, column, first_value)


def assess_selected_data(selected_data, column, first_value):
    assert column in selected_data.columns
    if first_value is not None:
        assert selected_data[column].iloc[1] == first_value  # Ensure the first value in the column matches the expected value
    else:
        assert pd.isna(selected_data[column].iloc[1])