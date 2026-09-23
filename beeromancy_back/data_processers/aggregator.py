import numpy as np
import pandas as pd

from .cleaner_utils import NUM_SELECTOR, get_most_common

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

def combine_master_names(df: pd.DataFrame, master_names: pd.DataFrame) -> pd.DataFrame:
    df['master_name'] = df.groupby(['brand', 'country'])['filter_name'].transform(lambda n: _get_master_names(n, master_names))

    columns_to_drop = [name for name in ['filter_name'] if name in df.columns]
    df.drop(columns=columns_to_drop, inplace=True)

    return df

def _get_master_names(names_series: pd.Series, names_references: pd.DataFrame) -> pd.Series:
    references = dict(zip(names_references["clean_name"], names_references["master_name"]))
    search_base = [*references.keys()]
    source = sorted(set(names_series.fillna('').to_list()), key=len)
    
    for name in source:
        references[name] = references.get(get_most_common(name, search_base), name)
        search_base.append(name)

    return names_series.fillna('').map(references)

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