import io
import json
from pathlib import Path

import pandas as pd

from .aggregator import combine_master_names, get_aggregated_ingredients
from .characteristics_extractor import extract_characteristics
from .raw_processer import get_base_cleaning, get_deep_cleaning

ITEM_TYPES = ['malt', 'hop', 'yeast']

class ScrapedDataProcesser:
    def __init__(self, local_output_path: Path | None = None):
        self.output_path = local_output_path
        self.entries_to_add = {t: None for t in ITEM_TYPES}
        self.entries_to_update = {t: None for t in ITEM_TYPES}

    def load_data(self, raw_data_json: io.textIOBase):
        self.raw_data = pd.json_normalize(json.load(raw_data_json))

    def process_data(self, existing_entries: pd.DataFrame):
        if self.raw_data.empty:
            print("No data loaded")
            return
        
        clean_data = get_base_cleaning(self.raw_data.copy())
        clean_data = clean_data.merge(existing_entries, how="left", on=["clean_name", "brand"])
                
        new_entries = clean_data[clean_data["master_name"].isna()].copy().reset_index(drop=True)
        if not new_entries.empty:
            new_entries = get_deep_cleaning(new_entries.copy())
            new_entries = combine_master_names(new_entries.copy(), existing_entries)

            existing_master_names = set(existing_entries['master_name'].dropna())
            new_master_names = set(new_entries['master_name'].dropna())
            to_add = new_master_names - existing_master_names
            to_update = new_master_names & existing_master_names

            for type in ITEM_TYPES:
                type_specific_data = extract_characteristics(new_entries[new_entries['item_type'] == type].copy(), type, str(self.output_path))
                type_specific_data = get_aggregated_ingredients(type_specific_data.copy())
                self.entries_to_add[type] = type_specific_data[type_specific_data['master_name'].isin(to_add)].copy()
                self.entries_to_update[type] = type_specific_data[type_specific_data['master_name'].isin(to_update)].copy()

        self.new_mapping = new_entries[new_entries['master_name'].isin(to_add)]['clean_name', 'master_name', 'id', 'brand']
        self.update_mapping = new_entries[new_entries['master_name'].isin(to_update)]['clean_name', 'master_name', 'id', 'brand']
