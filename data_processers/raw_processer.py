import json
import pandas as pd
import re

class ScrapedDataProcesser:
    def get_cleared_data(self, raw_data: str):
        self.raw_data = pd.json_normalize(json.load(raw_data))
        
        self._clear_strings()
        self._convert_names()

        self.raw_data['price'] = self.raw_data['price'].apply(lambda pr: round(float(pr), 2) if pr else None)
        
        self._convert_weights()

        return self.raw_data[['item_type','clean_name','source_domain', 'weight', 'units', 'price', 'currency', 'description', 'full_description', 'characteristics', 'additional_info', 'url']]
    

    def _clear_strings(self):
        df = self.raw_data

        strings = self.raw_data.select_dtypes(include=['string'])
        df[strings.columns] = strings.map(self._get_clean_string)

        df['characteristics'] = df['characteristics'].apply(lambda l: [self._get_clean_string(s) for s in l])


    def _get_clean_string(self, string: str):
        s = string.strip()
        s = re.sub(r'\s+', ' ', s)
        s= s.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
        s = re.sub(r'[\x00-\x1f\x7f]', '', s)
        return s.lower()

    def _convert_names(self):
        self.raw_data['name'] = self.raw_data['name'].apply(self._get_clear_name)
        self.raw_data[['clean_name', 'weight', 'units']] = self.raw_data['name'].str.split('|', expand=True)


    def _get_clear_name(self, raw_name: str):
        items = raw_name.split(',')
        
        name = items[0]
        weight = items[-1].strip() if len(items) > 1 else "0"
        unit = ''

        find = re.match(r'.*?(?P<w>\d+([.,]\d+)?)(?P<i>.*)', weight)
        if find:
            weight = find.group('w').replace(',', '.')
            unit = find.group('i').strip()
        unit = 'кг' if 'кг' in unit else 'г'
        
        if len(items) > 2:
            name = ' '.join(items[0:-2])
        
        name = re.sub(r'\s?\(.*?\)\s?', ' ', name)
        name = re.sub(r'^.*?[СсCc]олод\s?', '', name)
        name = re.sub(r'^.*?[Дд]рожжи\s?', '', name)
        name = re.sub(r'^.*?[Хх]мель\s?', '', name)

        return '|'.join([name, weight, unit])
    
    def _convert_weights(self):
        self.raw_data['weight'] = self.raw_data['weight'].apply(lambda w: float(w))
        mask = (self.raw_data['item_type']=='malt') & (self.raw_data['units']=='г')
        self.raw_data.loc[mask, 'weight'] = round(self.raw_data.loc[mask, 'weight'] / 1000, 2)
        self.raw_data.loc[mask, 'units'] = 'кг'


    def get_malts_characteristics(self, malts: pd.DataFrame):
        selectors = {
            'color': r"\b(?P<color>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?[eе][bв][cс]\b",
            'extract': r"экстракт.*?\b(?P<extract>\d+(?:[.,]\d+)?)\s?%",
            'protein': r"бело?ка?.*?\b(?P<protein>\d+(?:[.,]\d+)?)\s?%",
            'share': r"(?:засып|заклад).*?\b(?P<share>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'kolbach': r"кольбах.*?\b(?P<kolbach>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?",
            'diastatic': r"диастат.*?(?P<diastatic>\d+(?:[.,]\d+)?(?:\s*[-–—]\s*\d+(?:[.,]\d+)?)?(?:\s*(?:°?[lwk]|lintner)\b\w*)?)"
        }
        
        self._set_new_columns(malts, selectors, output_file='./outputs/malts_data.csv')

        return malts

    def get_hops_characteristics(self, hops: pd.DataFrame):
        selectors = {
            'alpha': r"альфа.*?\b(?P<alpha>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'beta': r"бета.*?\b(?P<beta>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'cohumulon': r"когум.*?\b(?P<cohumulon>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'oils': r"(?:масл|масел).*?\b(?P<oils>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?",
        }
        
        self._set_new_columns(hops, selectors, output_file='./outputs/hops_data.csv')
        
        return hops
    
    def get_yeasts_characteristics(self, yeasts: pd.DataFrame):
        selectors = {
            'attenuation': r"(?:сбраж|брож|аттен).*?\b(?P<attenuation>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'flocculation': r"флок.*?\b(?P<flocculation>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'fermentation_temperature': r"(?:темп|брож).*?\b(?P<fermentation_temperature>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?[°]?[CcСсFf]",
            'alcohol_tolerance': r"(?:спирт|алкогол).*?\b(?P<alcohol_tolerance>\d+(?:[.,]\d+)?(?:\s?[-–—]\s?\d+(?:[.,]\d+)?)?)\s?%",
            'diastatic': r"диастат.*?\b(?P<diastatic>полож|отриц).*?\b",
            'fenolic': r"фено.*?\b(?P<fenolic>полож|отриц).*?\b",
        }
        
        self._set_new_columns(yeasts, selectors, output_file='./outputs/yeasts_data.csv')
        
        return yeasts
    
    
    def _set_new_columns(self, df: pd.DataFrame, regex_selectors: dict, output_file: str = None):
        clean_characteristics = df['characteristics'].fillna('').str.join(' ')
        description_superstring = clean_characteristics + ' ' + df['full_description'].fillna('') + ' ' + df['additional_info'].fillna('') + ' ' + df['description'].fillna('')
        
        for column_name, sel in regex_selectors.items():
            df[column_name] = description_superstring.str.extract(sel)[column_name]

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                df.to_csv(f, sep='\t', encoding='utf-8', index=True, lineterminator='\n', header=True)

