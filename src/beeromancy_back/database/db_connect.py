import pandas as pd
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, joinedload

import beeromancy_back.database.db_schema as schema
from beeromancy_back.data_processers import PRODUCER_BASE_COUNTRIES

CHARACTERISTIC_CLASSES = {
    'malt': schema.Malt_Characteristics,
    'yeast': schema.Yeast_Characteristics,
    'hop': schema.Hop_Characteristics
}

class DatabaseController:
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
            select(schema.IngredientMapping.parser_name.label("clean_name"), schema.Ingredient.name.label("master_name"),
                   schema.IngredientMapping.ingr_id.label('id'), schema.Producer.name.label("brand"))
            .select_from(schema.IngredientMapping).join(schema.Ingredient).join(schema.Producer)
        )

        return pd.read_sql_query(q, con = self.engine)

    def get_ingredient_by_id(self, ingr_id: int):
        return self.session.get(
            schema.Ingredient,
            ingr_id,
            options=[
                joinedload(schema.Ingredient.category),
                joinedload(schema.Ingredient.producer),
                joinedload(schema.Ingredient.country)
            ]
        )

    def get_ingredients_by_type(self, ingr_type: str):
        q = (
            select(schema.Ingredient)
            .join(schema.IngrType)
            .where(schema.IngrType.name == ingr_type)
            .options(joinedload(schema.Ingredient.category),
                     joinedload(schema.Ingredient.producer),
                     joinedload(schema.Ingredient.country))
        )
        return self.session.scalars(q).all()

    def get_user_by_username(self, username: str):
        return self.session.scalars(
            select(schema.User)
            .where(schema.User.username == username)
        ).first()

    def try_prepare_for_loading(self, mapping: pd.DataFrame) -> bool:
        if mapping.empty:
            return False
        
        self.producer_cache = {p.name: p for p in self.session.scalars(select(schema.Producer)).all()}
        self.country_cache = {c.country_code: c for c in self.session.scalars(select(schema.Country)).all()}
        self.type_cache = {t.name: t for t in self.session.scalars(select(schema.IngrType)).all()}
        self.new_mapping = mapping

        return True


    def load_ingredients_from_df(self, ingredients: pd.DataFrame, category: str):
        if ingredients.empty:
            return

        if category not in self.type_cache:
            self.type_cache[category] = schema.IngrType(name = category)
        ingr_type = self.type_cache[category]

        chars_class = CHARACTERISTIC_CLASSES.get(category, None)
        if chars_class is None:
            raise ValueError(f"unknown characteristics type {category}")

        for _, ingr in ingredients.iterrows():
            c_name = ingr['country']
            if c_name not in self.country_cache:
                self.country_cache[c_name] = schema.Country(country_code = c_name, name = c_name)
            country = self.country_cache.get(c_name)
            
            prod_name = ingr['brand'].strip()
            if prod_name not in self.producer_cache:
                base_country = PRODUCER_BASE_COUNTRIES.get(prod_name, 'us')
                if base_country and base_country not in self.country_cache:
                    self.country_cache[base_country] = schema.Country(country_code = base_country, name = base_country)
                self.producer_cache[prod_name] = schema.Producer(name = prod_name, base_country=self.country_cache.get(base_country))
            producer = self.producer_cache.get(prod_name)

            ingr_orm = schema.Ingredient(
                name=ingr['master_name'],
                short_descr=ingr['description'],
                full_descr= ingr['full_description']
            )

            ingr_orm.category = ingr_type
            ingr_orm.producer = producer
            ingr_orm.country = country

            for _, entry in self.new_mapping[self.new_mapping['master_name']==ingr_orm.name].iterrows():
                ingr_orm.parser_names.append(schema.IngredientMapping(master_ingredient=ingr_orm, parser_name=entry['clean_name']))

            valid_cols = chars_class.__table__.columns.keys()
            args = {k: v for k, v in ingr.to_dict().items() if k in valid_cols}
            chars = chars_class(**args)
            chars.ref_ingr = ingr_orm
            self.session.add(chars)
            
            self.session.add(ingr_orm)

    def try_prepare_for_update(self, mapping: pd.DataFrame) -> bool:
        if mapping.empty:
            return False

        self.update_mapping = mapping
        self.ingr_orm_to_update = self.session.scalars(select(schema.Ingredient)
                                                   .where(schema.Ingredient.ingr_id.in_(self.update_mapping['id'].tolist()))).all()

        self.question_log = {}
        return True

    def update_ingredients_from_df(self, ingredients: pd.DataFrame, category: str):
        if ingredients.empty:
            return

        chars_class = CHARACTERISTIC_CLASSES.get(category)
        if chars_class is None:
            raise ValueError(f"unknown characteristics type {category}")

        chars_cols = chars_class.__table__.columns.keys()
        characteristics_list = self.session.scalars(select(chars_class).where(chars_class.ingr_id.in_([i.ingr_id for i in self.ingr_orm_to_update]))).all()
        characteristics = {c.ingr_id: c for c in characteristics_list}

        diff = {
            'Ingredient': [],
            'Characteristics': []
            }
        
        ingredients_indexed = ingredients.set_index('master_name')
        for ingr_orm in self.ingr_orm_to_update:
            need_update = False
            data = {'ingr_id': ingr_orm.ingr_id}
            self.question_log[ingr_orm.ingr_id] = {'name': ingr_orm.name}
            new_entry = ingredients_indexed.loc[ingr_orm.name].to_dict()

            for _, entry in self.update_mapping[self.update_mapping['id']==ingr_orm.ingr_id].iterrows():
                self.session.add(schema.IngredientMapping(master_ingredient=ingr_orm, parser_name=entry['clean_name']))

            if ingr_orm.short_descr != new_entry.get('description', None):
                self.question_log[ingr_orm.ingr_id]['description'] = {'db': ingr_orm.short_descr, 'new': new_entry.get('description', None)}

            if (ingr_orm.full_descr != new_entry.get('full_description', None)) and (not pd.isna(new_entry.get('full_description'))):
                if pd.isna(ingr_orm.full_descr):
                    need_update = True
                    data['full_descr'] = new_entry.get('full_description', None)
                else:
                    self.question_log[ingr_orm.ingr_id]['full_description'] = {'db': ingr_orm.full_descr, 'new': new_entry.get('full_description', None)}

            if need_update:
                diff['Ingredient'].append(data)


            chars_orm = characteristics.get(ingr_orm.ingr_id)
            if chars_orm is None:
                continue

            need_update = False
            data = {'ingr_id': ingr_orm.ingr_id}
            for c in chars_cols:
                if c=='ingr_id':
                    continue
                db_val = chars_orm.__getattribute__(c)
                new_val = new_entry.get(c, None)
                if db_val != new_val:
                    if pd.isna(db_val):
                        need_update = True
                        data[c] = new_val
                    else:
                        self.question_log[ingr_orm.ingr_id][c] = {'db': db_val, 'new': new_val}

            if need_update:
                diff['Characteristics'].append(data)

        if diff['Ingredient']:
            self.session.execute(update(schema.Ingredient), diff['Ingredient'])
        if diff['Characteristics']:
            self.session.execute(update(chars_class), diff['Characteristics'])
        