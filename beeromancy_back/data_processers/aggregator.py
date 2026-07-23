import pandas as pd
import numpy as np
from .data_cleaner import NUM_SELECTOR

PRIORITY_SOURCE = 'beer.rf'
TARGET_COLUMNS = ['clean_name', 'description', 'full_description']

CHARACTERISTICS = {
    'malt': {
        'num': ['color_ebc', 'share', 'extract', 'protein', 'kolbach', 'diastatic'],
        'val': []},
    'hop': {
        'num': ['alpha', 'beta', 'cohumulon', 'oils'],
        'val': []},
    'yeast': {
        'num': ['attenuation', 'ferment_temp', 'alco_tolerance'],
        'val': ['flocculation', 'diastatic', 'fenolic']}
}


def get_aggregated_ingredients(data_raw: pd.DataFrame) -> pd.DataFrame:

    for c in TARGET_COLUMNS:
        data_raw[f'priority_{c}'] = np.where(data_raw['source_domain'] == PRIORITY_SOURCE, data_raw[c], None)
    
    characteristics = CHARACTERISTICS.get(data_raw.iloc[0]['item_type'], {'num':[], 'val':[]})

    for char in characteristics['num']:
        extracted = data_raw[char].str.extract(_pattern_for_characteristic(char))
        data_raw[f"{char}_min"] = extracted[f"{char}_min"].astype(float)
        data_raw[f"{char}_max"] = extracted[f"{char}_max"].astype(float)

    aggr_setup = {
        'item_type': 'first',
        **{f"priority_{c}": 'first' for c in TARGET_COLUMNS},
        **{c: 'first' for c in TARGET_COLUMNS},
        'country': 'first',
        **{f"{c}_min": 'min' for c in characteristics['num']},
        **{f"{c}_max": 'max' for c in characteristics['num']},
        **{c: 'first' for c in characteristics['val']}
    }

    aggregated = data_raw.groupby(['brand', 'master_name']).agg(aggr_setup).reset_index()

    for c in TARGET_COLUMNS:
        aggregated[c] = aggregated[f'priority_{c}'].fillna(aggregated[c])

    aggregated.drop(columns = [f'priority_{c}' for c in TARGET_COLUMNS], inplace=True)
    return aggregated


def _pattern_for_characteristic(char_name: str) -> str:
    return fr"(?P<{char_name}_min>{NUM_SELECTOR})-(?P<{char_name}_max>{NUM_SELECTOR}) (?P<{char_name}_units>.*)"