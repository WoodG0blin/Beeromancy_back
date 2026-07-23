# Карта для приведения любых русскоязычных и англоязычных корней к коду ISO
COUNTRY_CLEAN_MAP = {
    'сша': 'us', 'us': 'us', 'usa': 'us', 'америк': 'us',
    'герман': 'de', 'de': 'de', 'germany': 'de', 'немец': 'de',
    'чехи': 'cz', 'cz': 'cz', 'czech': 'cz', 'жатец': 'cz',
    'великобр': 'gb', 'uk': 'gb', 'англия': 'gb', 'британ': 'gb', 'england': 'gb',
    'росси': 'ru', 'ru': 'ru', 'чуваш': 'ru', 'курск': 'ru', 'отечеств': 'ru',
    'белг': 'be', 'belg': 'be', 'chateau': 'be', 'бельги': 'be',
    'австрал': 'au', 'au': 'au', 'australia': 'au',
    'новозел': 'nz', 'nz': 'nz', 'new zealand': 'nz',
    'китай': 'ch'
}

# Регулярное выражение для поиска кодов или корней как отдельных слов в названии товара
COUNTRY_PATTERN = r'\b(' + '|'.join(COUNTRY_CLEAN_MAP.keys()) + r')'

# Резервный справочник кодов стран для сортов хмеля (если в имени и бренде пусто)
HOPS_DEFAULT_COUNTRIES = {
    'citra': 'us', 'mosaic': 'us', 'amarillo': 'us', 'simcoe': 'us', 'cascade': 'us',
    'galaxy': 'au', 'vic secret': 'au',
    'saaz': 'cz', 'жатецкий': 'cz',
    'tradition': 'de', 'perle': 'de', 'magnum': 'de',
    'mandarina bavaria': 'de', 'mittelfruh': 'de', 'mittelfrüh': 'de',
    'golding': 'gb', 'fuggle': 'gb',
    'подвязный': 'ru', 'ранний зеленый': 'ru'
}

# Справочник базовых кодов стран для производителей
PRODUCER_BASE_COUNTRIES = {
    # --- СОЛОД / ЗЕРНО / ДОБАВКИ ---
    'грейнрус': 'ru',
    'ностерс': 'ru',          # Nosters (Россия)
    'weyermann': 'de',        # Германия
    'castle malting': 'be',   # Бельгия
    'агроресурсы': 'ru',      # Агроресурсы (Россия)
    'ireks': 'de',            # Ирекс (Германия)
    'староминский солод': 'ru', # Россия

    # --- ДРОЖЖИ ---
    'fermentis': 'fr',        # Ферментис (Франция, дочка Lesaffre)
    'lallemand': 'ca',        # Лаллеманд (Канада, штаб-квартира и корни)
    'bragman': 'gb',          # Брагман (Великобритания)
    'mangrove jacks': 'nz',   # Мангров Джекс (Новая Зеландия)
    'angel yeast': 'cn',      # Ангел (Китай)

    # --- ХМЕЛЬ (ТРЕЙДЕРЫ, АССОЦИАЦИИ И БРЕНДЫ) ---
    'yakima valley': 'us',     # Yakima Valley Hops (США)
    'barthhaas': 'de',         # Барth-Хаас (Германия, головной офис холдинга)
    'yakima chief hops': 'us', # Якима Чиф (США)
    'spalter hopfen': 'de',    # Шпальтер Хопфен (Германия, кооператив Шпальт)
    'hvg': 'de',               # Немецкий хмелевой кооператив Hallertau (Германия)
    'charles faram': 'gb',     # Чарльз Фарам (Великобритания)
    'powisle': 'pl',           # Повисле (Польша)
    'glacier hops': 'us',      # Глейшер Хопс (США)
    '47 hops': 'us',           # 47 Хопс (США)
    'hpa': 'au',               # Hop Products Australia (Австралия)
    'nz hops': 'nz',           # New Zealand Hops (Новая Зеландия)
    'jmhopscz': 'cz',          # Жатэцкие хмелеводы (Чехия)
    'чувашхмельпром оао': 'ru', # Россия

    # --- ЛОКАЛЬНЫЕ БРЕНДЫ, НАБОРЫ, ФАСОВЩИКИ И ДИСТРИБЬЮТОРЫ ---
    'ign': 'ru',               # ИГН / Хмель и Солод (Россия)
    'leyka': 'ru',             # Лейка (Россия)
    'asp lab': 'ru',           # АСП Лаб (Россия)
    'beervingem': 'ru',        # Бирвингем (Российский бренд наборов/фасовки)
    'beergineer': 'ru',        # Биржинир (Россия)
    'nomikai': 'ru',           # Номикаи (Россия)
    'cls': 'ru',               # ЦЛС / Логистические системы (Россия)
    'mm-invest': 'ru'          # ММ-Инвест (Россия)
}