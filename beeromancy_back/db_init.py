import sqlite3

def create_brewery_db():
    connect = sqlite3.connect('beeromancy.db')
    cursor = connect.cursor()

    cursor.execute('PRAGMA foreign_keys = ON;') #for sqlite - enabling foreign keys

    #DIMENSION TABLES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_users(
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE);
    ''')

    # snowflake dim tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_producers(
            producer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_countries(
            country_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_shops(
            shop_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_url TEXT NOT NULL UNIQUE);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_ingr_types(
            ingr_type INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE);
    ''')

    # ingredients dim tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_ingredients(
            ingr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingr_type INTEGER,
            name TEXT NOT NULL,
            producer_id INTEGER,
            country_id INTEGER,
            short_descr TEXT NOT NULL,
            full_descr TEXT,
            FOREIGN KEY(ingr_type) REFERENCES dim_ingr_types(ingr_type) ON DELETE RESTRICT);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_malt_characteristics(
            ingr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            color_ebc_min REAL NOT NULL,
            color_ebc_max REAL NOT NULL,
            share_min REAL,
            share_max REAL,
            extract_min REAL,
            extract_max REAL,
            protein_min REAL,
            protein_max REAL,
            kolbach_min REAL,
            kolbach_max REAL,
            diastatic INT,
            FOREIGN KEY(ingr_id) REFERENCES dim_ingredients(ingr_id) ON DELETE CASCADE);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_hop_characteristics(
            ingr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alpha_min REAL NOT NULL,
            alpha_max REAL NOT NULL,
            beta_min REAL,
            beta_max REAL,
            cohumulon_min REAL,
            cohumulon_max REAL,
            oils_min REAL,
            oils_max REAL,
            FOREIGN KEY(ingr_id) REFERENCES dim_ingredients(ingr_id) ON DELETE CASCADE);
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_yeast_characteristics(
            ingr_id INTEGER PRIMARY KEY AUTOINCREMENT,
            attenuation_min REAL NOT NULL,
            attenuation_max REAL NOT NULL,
            flocculation INTEGER,
            ferment_temp_min REAL,
            ferment_temp_max REAL,
            alco_tolerance_min REAL,
            alco_tolerance_max REAL,
            diastatic INTEGER,
            fenolic INTEGER,
            FOREIGN KEY(ingr_id) REFERENCES dim_ingredients(ingr_id) ON DELETE CASCADE);
    ''')

    # phases dim dable
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_phases(
            phase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            step_order INT NOT NULL,
            duration_adv_min INTEGER,
            duration_adv_max INTEGER,
            temp_adv_min INTEGER,
            temp_adv_max INTEGER);
    ''')

    # FACT TABLES
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_recipes(
            recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_recipe_id INTEGER,
            user_id INTEGER,
            name TEXT NOT NULL,
            descr TEXT,
            rating REAL DEFAULT 0.0,
            is_published INTEGER DEFAULT 0,
            status INTEGER,
            FOREIGN KEY(parent_recipe_id) REFERENCES fact_recipes(recipe_id) ON DELETE SET NULL,
            FOREIGN KEY(user_id) REFERENCES dim_users(user_id) ON DELETE SET NULL);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_recipe_ingredients(
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingr_id INTEGER NOT NULL,
            phase_id INTEGER NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY(recipe_id) REFERENCES fact_recipes(recipe_id) ON DELETE CASCADE,
            FOREIGN KEY(ingr_id) REFERENCES dim_ingredients(ingr_id) ON DELETE RESTRICT,
            FOREIGN KEY(phase_id) REFERENCES dim_phases(phase_id) ON DELETE RESTRICT);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_recipe_stages(
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            phase_id INTEGER NOT NULL,
            duration REAL NOT NULL,
            temp REAL,
            FOREIGN KEY(recipe_id) REFERENCES fact_recipes(recipe_id) ON DELETE CASCADE,
            FOREIGN KEY(phase_id) REFERENCES dim_phases(phase_id) ON DELETE RESTRICT);
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fact_prices(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingr_id INTEGER NOT NULL,
            shop_id INTEGER NOT NULL,
            package_weight REAL NOT NULL,
            price REAL,
            datestamp DATE NOT NULL,
            FOREIGN KEY(ingr_id) REFERENCES dim_ingredients(ingr_id) ON DELETE CASCADE,
            FOREIGN KEY(shop_id) REFERENCES dim_shops(shop_id) ON DELETE CASCADE);
    ''')

    ingr_types = [('malt',), ('hop',), ('yeast',), ('other',)]
    cursor.executemany('INSERT OR IGNORE INTO dim_ingr_types(name) VALUES (?)', ingr_types)

    connect.commit()
    connect.close()

if __name__ == '__main__':
    create_brewery_db()

    

