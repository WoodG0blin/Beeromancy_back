import json
import pandas as pd


class ContentController:
    def __init__(self, data_path: str):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.data = pd.json_normalize(self.config)
        self.data_unchecked = set()
        if not self.data.empty:
            self.data_unchecked = set(self.data['name'].values)
        print(self.data.head())

    def check_item(self, item):
        if item.name in self.data_unchecked:
            self.data_unchecked.remove(item.name)
            item_data = self.data[self.data['name'] == item.name].iloc[0]
            for field in item.fields():
                if field.name != 'price' and field.name in item_data:
                    val = item_data[field.name]
                    if isinstance(val, (list, dict)):
                        setattr(item, field.name, val)
                    elif not pd.isna(val):
                        setattr(item, field.name, val)
                    setattr(item, 'update_status', 'UPD')
            return True
        return False