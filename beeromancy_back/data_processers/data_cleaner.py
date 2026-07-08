import re

def get_clean_string(string: str) -> str:
    s = string.strip()
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('\xa0', ' ').replace('\u200b', '').replace('\ufeff', '')
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    s = re.sub(r'[-–—]', '-', s)
    return s.lower()

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
    
    name = re.sub(r'\s?\(.*?\)\s?', '', name)
    name = re.sub(r'^.*?[СсCc]олод\s?', '', name)
    name = re.sub(r'^.*?[Дд]рожжи\s?', '', name)
    name = re.sub(r'^.*?[Хх]мель\s?', '', name)

    return '|'.join([name, weight, unit])

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