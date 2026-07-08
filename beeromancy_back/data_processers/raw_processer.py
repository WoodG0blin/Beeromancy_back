import json
import io
import pandas as pd
from .data_cleaner import get_clean_string, get_clean_name, get_clean_characteristic, NUM_SELECTOR

class ScrapedDataProcesser:
    def get_cleared_data(self, raw_data_json: io.textIOBase):
        raw_data = pd.json_normalize(json.load(raw_data_json))

        strings = raw_data.select_dtypes(include=['string'])
        raw_data[strings.columns] = strings.map(get_clean_string)

        raw_data['characteristics'] = raw_data['characteristics'].apply(lambda l: [get_clean_string(s) for s in l])
        raw_data['name'] = raw_data['name'].apply(get_clean_name)
        raw_data[['clean_name', 'weight', 'units']] = raw_data['name'].str.split('|', expand=True)
        raw_data['price'] = raw_data['price'].apply(lambda pr: round(float(pr), 2) if pr else None)

        raw_data['weight'] = raw_data['weight'].apply(lambda w: float(w))
        mask = (raw_data['item_type']=='malt') & (raw_data['units']=='г')
        raw_data.loc[mask, 'weight'] = round(raw_data.loc[mask, 'weight'] / 1000, 2)
        raw_data.loc[mask, 'units'] = 'кг'

        return raw_data[['item_type','clean_name','source_domain', 'weight', 'units', 'price', 'currency', 'description', 'full_description', 'characteristics', 'additional_info', 'url']]
    

    RANGE_SELECTOR = NUM_SELECTOR + r"\s?(?:[^\d-]*-\s?" + NUM_SELECTOR + r")?"

    def get_malts_characteristics(self, malts: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        selectors = {
            'color': r"\b(?P<color>" + self.RANGE_SELECTOR + r"\s?[eе][bв][cс]\b)",
            'extract': r"экстракт[^;]*?\b(?P<extract>" + self.RANGE_SELECTOR + r"\s?%)",
            'protein': r"бело?ка?[^;]*?\b(?P<protein>" + self.RANGE_SELECTOR + r"\s?%)",
            'share': r"(?:засып|заклад)[^;]*?\b(?P<share>" + self.RANGE_SELECTOR + r"\s?%)",
            'kolbach': r"кольбах[^;]*?\b(?P<kolbach>" + self.RANGE_SELECTOR + r")\s?",
            'diastatic': r"диастат[^;]*?(?P<diastatic>" + self.RANGE_SELECTOR + r"(?:\s*(?:°?[lwk]|lintner)\b\w*)?)"
        }
        
        path = (outputs_path + "/malts_data.csv") if outputs_path else None
        return self._set_new_columns(malts.copy(), selectors, output_file=path)


    def get_hops_characteristics(self, hops: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        selectors = {
            'alpha': r"альфа[^;]*?\b(?P<alpha>" + self.RANGE_SELECTOR + r"\s?%)",
            'beta': r"бета[^;]*?\b(?P<beta>" + self.RANGE_SELECTOR + r"\s?%)",
            'cohumulon': r"когум[^;]*?\b(?P<cohumulon>" + self.RANGE_SELECTOR + r"\s?%)",
            'oils': r"(?:масл|масел)[^;]*?\b(?P<oils>" + self.RANGE_SELECTOR + r")\s?",
        }
        
        path = (outputs_path + "/hops_data.csv") if outputs_path else None
        return self._set_new_columns(hops.copy(), selectors, output_file=path)


    def get_yeasts_characteristics(self, yeasts: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        selectors = {
            'attenuation': r"(?:сбраж|брож|аттен)[^;]*?\b(?P<attenuation>" + self.RANGE_SELECTOR + r"\s?%)",
            'flocculation': r"флок[^;]*?\b(?P<flocculation>(?:низк|сред|высок)[^;]*?\b)",
            'fermentation_temperature': r"(?:темп|брож)[^;]*?\b(?P<fermentation_temperature>" + self.RANGE_SELECTOR + r"\s?[°]?[CcСсFf])",
            'alcohol_tolerance': r"(?:спирт|алкогол)[^;]*?\b(?P<alcohol_tolerance>" + self.RANGE_SELECTOR + r"\s?%)",
            'diastatic': r"диастат[^;]*?\b(?P<diastatic>(?:полож|отриц)[^;]*?\b)",
            'fenolic': r"фено[^;]*?\b(?P<fenolic>(?:полож|отриц)[^;]*?\b)",
        }
        
        path = (outputs_path + "/yeasts_data.csv") if outputs_path else None
        return self._set_new_columns(yeasts.copy(), selectors, output_file=path)
            
    
    def _set_new_columns(self, df: pd.DataFrame, regex_selectors: dict, output_file: str = None) -> pd.DataFrame:
        clean_characteristics = df['characteristics'].fillna('').str.join(';')
        description_superstring = clean_characteristics + ';' + df['full_description'].fillna('') + ';' + df['additional_info'].fillna('') + ';' + df['description'].fillna('')
        
        for column_name, sel in regex_selectors.items():
            df[column_name] = description_superstring.str.extract(sel)[column_name].apply(get_clean_characteristic)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                df.to_csv(f, sep='\t', encoding='utf-8', index=True, lineterminator='\n', header=True)
        
        return df
