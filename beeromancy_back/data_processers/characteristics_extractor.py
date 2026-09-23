
import numpy as np
import pandas as pd

from .cleaner_utils import NUM_SELECTOR, get_clean_characteristic

RANGE_SELECTOR = NUM_SELECTOR + r"\s?(?:[^\d;-]{0,10}-\s?" + NUM_SELECTOR + r")?"

CHARACTERISTICS_PARAMS = {
    'malt': {
        'color_ebc': {'keywords': r"", 'units': r"\s?[eе][bв][cс]\b", 'specific_search': None},
        'extract': {'keywords': r"экстракт", 'units': r"\s?%", 'specific_search': None},
        'protein': {'keywords': r"бело?ка?", 'units': r"\s?%", 'specific_search': None},
        'share': {'keywords': r"(?:засып|заклад)", 'units': r"\s?%", 'specific_search': None},
        'kolbach': {'keywords': r"кольбах", 'units': r"", 'specific_search': None},
        'diastatic': {'keywords': r"диастат", 'units': r"(?:\s*(?:°?[lwk]|lintner)\b\w*)?", 'specific_search': None},
    },
    'hop': {
        'alpha': {'keywords': r"альфа", 'units': r"\s?%", 'specific_search': None},
        'beta': {'keywords': r"бета", 'units': r"\s?%", 'specific_search': None},
        'cohumulon': {'keywords': r"когум", 'units': r"\s?%", 'specific_search': None},
        'oils': {'keywords': r"(?:масл|масел)", 'units': r"", 'specific_search': None},
    },
    'yeast': {
        'attenuation': {'keywords': r"(?:сбраж|брож|аттен)", 'units': r"\s?%", 'specific_search': None},
        'flocculation': {'keywords': r"флок", 'units': r"", 'specific_search': r"(?:низк|сред|высок)\w*"},
        'ferment_temp': {'keywords': r"(?:темп|брож)", 'units': r"\s?[°]?[CcСсFf]", 'specific_search': None},
        'alco_tolerance': {'keywords': r"(?:спирт|алкогол)", 'units': r"\s?%", 'specific_search': None},
        'diastatic': {'keywords': r"диастат", 'units': r"", 'specific_search': r"(?:полож|отриц)\w*"},
        'fenolic': {'keywords': r"фено", 'units': r"", 'specific_search': r"(?:полож|отриц)\w*"},
    }
}

def extract_characteristics(df: pd.DataFrame, item_type: str, outputs_path: str | None = None) -> pd.DataFrame:
    parameters = CHARACTERISTICS_PARAMS.get(item_type, {})
    path = (outputs_path + f"/{item_type}_data.csv") if outputs_path else None
    return _set_new_columns(df.copy(), parameters, output_file=path)
            
    
def _set_new_columns(df: pd.DataFrame, regex_params: dict, output_file: str | None = None) -> pd.DataFrame:
    clean_characteristics = df['characteristics'].fillna('').apply(lambda l: ';'.join(l) if isinstance(l, list) else str(l))

    list_sep = r"[^;]*?"
    desc_sep = r".{0,100}?"

    for characteristic, config in regex_params.items():
        key = config['keywords']
        unit = config['units']
        spec = config['specific_search']
        sel_list = key + list_sep + r"\b(?P<" + characteristic + r">" + ((spec + list_sep) if spec else RANGE_SELECTOR) + unit + r")"
        sel_desc = key + desc_sep + r"\b(?P<" + characteristic + r">" + ((spec + desc_sep) if spec else RANGE_SELECTOR) + unit + r")"

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
    
    # if output_file:
    #     with open(output_file, 'w', encoding='utf-8') as f:
    #         df.to_csv(f, sep='\t', encoding='utf-8', index=True, lineterminator='\n', header=True)
    
    return df