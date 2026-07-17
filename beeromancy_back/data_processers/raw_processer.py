import json
import io
import pandas as pd
import numpy as np
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

        return raw_data[['item_type','clean_name', 'brand', 'country', 'subtype', 'source_domain', 'weight', 'units', 'price', 'currency', 'description', 'full_description', 'characteristics', 'additional_info', 'url']]
        # replace when update status will be added
        return raw_data[['item_type','clean_name', 'brand', 'country', 'subtype', 'source_domain', 'weight', 'units', 'price', 'currency', 'description', 'full_description', 'characteristics', 'additional_info', 'url', 'update_status']]
    

    RANGE_SELECTOR = NUM_SELECTOR + r"\s?(?:[^\d;-]{0,10}-\s?" + NUM_SELECTOR + r")?"
    
    def get_malts_characteristics(self, malts: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        parameters = {
            'color': {'keywords': r"", 'units': r"\s?[eе][bв][cс]\b", 'specific_search': None},
            'extract': {'keywords': r"экстракт", 'units': r"\s?%", 'specific_search': None},
            'protein': {'keywords': r"бело?ка?", 'units': r"\s?%", 'specific_search': None},
            'share': {'keywords': r"(?:засып|заклад)", 'units': r"\s?%", 'specific_search': None},
            'kolbach': {'keywords': r"кольбах", 'units': r"", 'specific_search': None},
            'diastatic': {'keywords': r"диастат", 'units': r"(?:\s*(?:°?[lwk]|lintner)\b\w*)?", 'specific_search': None},
        }
        
        path = (outputs_path + "/malts_data.csv") if outputs_path else None
        return self._set_new_columns(malts.copy(), parameters, output_file=path)


    def get_hops_characteristics(self, hops: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        parameters = {
            'alpha': {'keywords': r"альфа", 'units': r"\s?%", 'specific_search': None},
            'beta': {'keywords': r"бета", 'units': r"\s?%", 'specific_search': None},
            'cohumulon': {'keywords': r"когум", 'units': r"\s?%", 'specific_search': None},
            'oils': {'keywords': r"(?:масл|масел)", 'units': r"", 'specific_search': None},
        }
        
        path = (outputs_path + "/hops_data.csv") if outputs_path else None
        return self._set_new_columns(hops.copy(), parameters, output_file=path)


    def get_yeasts_characteristics(self, yeasts: pd.DataFrame, outputs_path: str = None) -> pd.DataFrame:
        parameters = {
            'attenuation': {'keywords': r"(?:сбраж|брож|аттен)", 'units': r"\s?%", 'specific_search': None},
            'flocculation': {'keywords': r"флок", 'units': r"", 'specific_search': r"(?:низк|сред|высок)\w*"},
            'fermentation_temperature': {'keywords': r"(?:темп|брож)", 'units': r"\s?[°]?[CcСсFf]", 'specific_search': None},
            'alcohol_tolerance': {'keywords': r"(?:спирт|алкогол)", 'units': r"\s?%", 'specific_search': None},
            'diastatic': {'keywords': r"диастат", 'units': r"", 'specific_search': r"(?:полож|отриц)\w*"},
            'fenolic': {'keywords': r"фено", 'units': r"", 'specific_search': r"(?:полож|отриц)\w*"},
        }
        
        path = (outputs_path + "/yeasts_data.csv") if outputs_path else None
        return self._set_new_columns(yeasts.copy(), parameters, output_file=path)
            
    
    def _set_new_columns(self, df: pd.DataFrame, regex_params: dict, output_file: str = None) -> pd.DataFrame:
        clean_characteristics = df['characteristics'].fillna('').apply(lambda l: ';'.join(l) if isinstance(l, list) else str(l))

        list_sep = r"[^;]*?"
        desc_sep = r".{0,100}?"

        for characteristic, config in regex_params.items():
            key = config['keywords']
            unit = config['units']
            spec = config['specific_search']
            sel_list = key + list_sep + r"\b(?P<" + characteristic + r">" + ((spec + list_sep) if spec else self.RANGE_SELECTOR) + unit + r")"
            sel_desc = key + desc_sep + r"\b(?P<" + characteristic + r">" + ((spec + desc_sep) if spec else self.RANGE_SELECTOR) + unit + r")"

            res_from_list = clean_characteristics.str.extract(sel_list)[characteristic]
            res_from_full_desc = df['full_description'].fillna('').str.extract(sel_desc)[characteristic]
            res_from_desc = df['description'].fillna('').str.extract(sel_desc)[characteristic]
            res_from_add_info = df['additional_info'].fillna('').str.extract(sel_desc)[characteristic]

            conditions = [res_from_list.notna(), res_from_full_desc.notna(), res_from_desc.notna(), res_from_add_info.notna()]
            choices = [res_from_list, res_from_full_desc, res_from_desc, res_from_add_info]

            res = np.select(conditions, choices, default=None)

            df[characteristic] = pd.Series(res, index = df.index).apply(lambda s: get_clean_characteristic(s) if pd.notna(s) else None)

        columns_to_drop = [name for name in ['characteristics', 'additional_info'] if name in df.columns]

        df.drop(columns=columns_to_drop, inplace=True)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                df.to_csv(f, sep='\t', encoding='utf-8', index=True, lineterminator='\n', header=True)
        
        return df