import pandas as pd
from sqlalchemy import ForeignKey, select, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import db_schema as schema
from data_processers import PRODUCER_BASE_COUNTRIES

class DatabaseController():
    def __init__(self):
        self.engine = create_engine("sqlite:///beeromancy.db", echo=False)
        schema.Base.metadata.create_all(bind=self.engine)


    def __enter__(self):
        self.session = Session(self.engine)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'session') and self.session:
            if exc_type is not None:
                self.session.rollback()  # Откатываем, если была ошибка
                print(f"[DB] Транзакция отменена из-за ошибки: {exc_val}")
            else:
                self.session.commit()
            self.session.close()

    def get_ingredients_mapping(self) -> pd.DataFrame:
        q = (
            select(schema.IngredientMapping.parser_name.label("clean_name"), schema.Ingredient.name.label("master_name"), schema.Producer.name.label("brand"))
            .select_from(schema.IngredientMapping).join(schema.Ingredient).join(schema.Producer)
        )

        return pd.read_sql_query(q, con = self.session.bind)

    def load_ingredients_from_df(self, ingredients: pd.DataFrame, mapping: pd.DataFrame):
        producer_cache = {p.name: p for p in self.session.scalars(select(schema.Producer)).all()}
        country_cache = {c.country_code: c for c in self.session.scalars(select(schema.Country)).all()}
        type_cache = {t.name: t for t in self.session.scalars(select(schema.IngrType)).all()}

        category = ingredients.iloc[0]['item_type']
        if category not in type_cache:
            type_cache[category] = schema.IngrType(name = category)
        ingr_type = type_cache[category]

        chars_classes = {
            'malt': schema.Malt_Characteristics,
            'yeast': schema.Yeast_Characteristics,
            'hop': schema.Hop_Characteristics
        }
        chars_class = chars_classes.get(category, None)

        for _, ingr in ingredients.iterrows():
            c_name = ingr['country']
            if c_name not in country_cache:
                country_cache[c_name] = schema.Country(country_code = c_name, name = c_name)
            country = country_cache.get(c_name)
            
            prod_name = ingr['brand'].strip()
            if prod_name not in producer_cache:
                base_country = PRODUCER_BASE_COUNTRIES.get(prod_name, 'us')
                if base_country and base_country not in country_cache:
                    country_cache[base_country] = schema.Country(country_code = base_country, name = base_country)
                producer_cache[prod_name] = schema.Producer(name = prod_name, base_country=country_cache.get(base_country))
            producer = producer_cache.get(prod_name)

            ingr_orm = schema.Ingredient(
                name=ingr['clean_name'],
                short_descr=ingr['description'],
                full_descr= ingr['full_description']
            )

            ingr_orm.category = ingr_type
            ingr_orm.producer = producer
            ingr_orm.country = country

            valid_cols = chars_class.__table__.columns.keys()
            args = {k: v for k, v in ingr.to_dict().items() if k in valid_cols}
            chars = chars_class(**args)
            chars.ref_ingr = ingr_orm
            self.session.add(chars)

            current_mapping = mapping[(mapping['brand']==prod_name) & (mapping['master_name']==ingr['master_name'])].copy()
            current_mapping.drop_duplicates(subset=['brand','clean_name'], inplace=True, keep=False)
            for _, entry in current_mapping.iterrows():
                m = schema.IngredientMapping(master_ingredient=ingr_orm, parser_name=entry['clean_name'])
                # m.master_ingredient = ingr_orm
            
            self.session.add(ingr_orm)
