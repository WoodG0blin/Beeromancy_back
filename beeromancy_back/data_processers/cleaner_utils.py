import re
import string
from rapidfuzz import fuzz

def get_clean_string(string: str) -> str:
    s = string.strip()
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    s = re.sub(r'[-–—]', '-', s)
    return _homoglyph_filter(s.lower())

def get_clean_name(raw_name: str) -> str:
    items = raw_name.split(',')
    
    name = items[0]

    weight = "0"
    if len(items) > 1:
        for i in range(1, len(items)):
            if items[-i]:
                weight = items[-i].strip()
                break

    unit = ''

    find = re.match(r'.*?(?P<w>\d+([.,]\d+)?)(?P<i>.*)', weight)
    if find:
        weight = find.group('w').replace(',', '.')
        unit = find.group('i').strip()
    unit = 'кг' if 'кг' in unit else 'г'
    
    if len(items) > 2:
        name = get_clean_string(' '.join(items[0:-2]))
    
    return '|'.join([name.strip(), weight, unit])

def clean_with_dictionary(raw_name:str, source: dict, split_pattern: str = r'.*') -> str:
    name_set = {source.get(part, part) for part in re.findall(split_pattern, raw_name)}
    return ' '.join(sorted(list(name_set)))
        


NUM_SELECTOR = r"\d+(?:[.,]\d+)?"

def get_clean_characteristic(value: str) -> str:
    if isinstance(value, str):
        value = value.replace(' ', '').replace(',', '.').strip()
        
        selector = (
            r"^(?P<min>" + NUM_SELECTOR + r")"
            r"(?:[^\d-]*-(?P<max>" + NUM_SELECTOR + r"))?"
            r"(?P<units>[a-zA-Zа-яА-Я%°]+)?"
        )
        
        search = re.search(selector, value)
        if search:
            res = str(round(float(search.group('min')), 1))
            max_val = search.group('max')
            if max_val:
                res += f"-{round(float(max_val), 1)}"
            units = search.group('units')
            if units:
                res += f" {units.strip()}"
            return res
        else:
            return value
    else:
        return value

def get_most_common(st: str, base: list, comp_value: int = 80) -> str:
    if not base:
        return st
    
    comparison = [(compare_with_numbers(st, entry), entry) for entry in base]
    max_ind, result = max(comparison)
    return result if max_ind >= comp_value else st

def compare_with_numbers(st1: str, st2: str) -> int:
    st1_nums = set(re.findall(r'\d+', st1))
    st2_nums = set(re.findall(r'\d+', st2))

    if st1_nums != st2_nums:
        return 0
    else:
        return fuzz.token_sort_ratio(st1, st2)

def _homoglyph_filter(text:str)-> str:
    if not text:
        return ""
    
    homoglyphs = {
        'c': 'с', 'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 
        'x': 'х', 'y': 'у', 'k': 'к', 'm': 'м', 'h': 'н'
    }
    
    words = text.split()
    fixed_words = []
    
    for word in words:
        rus_count = len(re.findall(r'[а-яА-ЯёЁ]', word))
        eng_count = len(re.findall(r'[a-zA-Z]', word))
        
        if rus_count > eng_count:
            for eng, rus in homoglyphs.items():
                word = word.replace(eng, rus)
        else:
            for eng, rus in homoglyphs.items():
                word = word.replace(rus, eng)
        fixed_words.append(word)
            
    return " ".join(fixed_words)