import re
import pandas as pd
from .cleaner_utils import get_clean_string, get_clean_name, clean_with_dictionary
from .names_subs import NAMES_SUBSTITUTIONS, BRANDS_SUBS
from .countries_config import COUNTRY_CLEAN_MAP, COUNTRY_PATTERN, HOPS_DEFAULT_COUNTRIES, PRODUCER_BASE_COUNTRIES

def get_base_cleaning(raw_data: pd.DataFrame) -> pd.DataFrame:
    strings = raw_data.select_dtypes(include=['string'])
    raw_data[strings.columns] = strings.map(get_clean_string)

    raw_data['characteristics'] = raw_data['characteristics'].fillna('').apply(lambda l: [get_clean_string(s) for s in l])
    raw_data['name'] = raw_data['name'].fillna('').apply(get_clean_name)
    raw_data[['clean_name', 'weight', 'units']] = raw_data['name'].str.split('|', expand=True)
    raw_data['price'] = raw_data['price'].apply(lambda pr: round(float(pr), 2) if pr else None)

    raw_data["clean_name"] = raw_data['clean_name'].fillna('')

    raw_data['weight'] = raw_data['weight'].apply(lambda w: float(w))
    mask = (raw_data['item_type']=='malt') & (raw_data['units']=='г')
    raw_data.loc[mask, 'weight'] = round(raw_data.loc[mask, 'weight'] / 1000, 2)
    raw_data.loc[mask, 'units'] = 'кг'

    return raw_data[['item_type','clean_name', 'brand', 'country', 'subtype', 'source_domain', 'weight', 'units', 'price', 'currency', 'description', 'full_description', 'characteristics', 'additional_info', 'url']]


def get_deep_cleaning(raw_data: pd.DataFrame) -> pd.DataFrame:
    raw_data["brand"] = raw_data['brand'].fillna('')
    raw_data['filter_name'] = [_get_names_cleaned_from_brand(n, b, i) for n, b, i in zip(raw_data["clean_name"], raw_data["brand"], raw_data.index)]

    raw_data['brand'] = raw_data['brand'].apply(lambda b: clean_with_dictionary(raw_name=b, source=BRANDS_SUBS))

    raw_data['country'] = _resolve_countries(raw_data.copy())

    return raw_data


def _get_names_cleaned_from_brand(name: str, brand: str, ind) -> str:
    cleaned_name = clean_with_dictionary(name, NAMES_SUBSTITUTIONS, split_pattern=r'\w+')

    # cleaned_name = re.sub(r'\s?\(.*?\)\s?', '', cleaned_name)
    cleaned_name = re.sub(r'\s?\b[СсCc]олод\b\s?', ' ', cleaned_name)
    cleaned_name = re.sub(r'\s?\b[Дд]рожжи\b\s?', ' ', cleaned_name)
    cleaned_name = re.sub(r'\s?\b[Хх]мель\b\s?', ' ', cleaned_name)

    if not brand:
        return cleaned_name

    for word in brand.split():
        selector = rf"\s*\b{re.escape(word)}\b\s*"
        cleaned_name = re.sub(selector, ' ', cleaned_name)

    return cleaned_name


def _resolve_countries(df: pd.DataFrame) -> pd.Series:
    df['country_raw'] = df['clean_name'].str.extract(COUNTRY_PATTERN)
    df['op1'] = df['country_raw'].map(COUNTRY_CLEAN_MAP)

    df['op2'] = df['country'].fillna('').map(COUNTRY_CLEAN_MAP)

    hop_pattern = r'\b(' + '|'.join(HOPS_DEFAULT_COUNTRIES.keys()) + r')\b'
    df['hop_pattern'] = df['clean_name'].str.extract(hop_pattern)
    df['op3'] = df['hop_pattern'].map(HOPS_DEFAULT_COUNTRIES)

    df['op4'] = df['brand'].map(PRODUCER_BASE_COUNTRIES)

    return df['op1'].fillna(df['op2']).fillna(df['op3']).fillna(df['op4']).fillna('us')
        
