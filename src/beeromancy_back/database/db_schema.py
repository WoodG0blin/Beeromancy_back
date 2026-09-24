
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Country(Base):
    __tablename__ = "dim_countries"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str]

    producers: Mapped[list[Producer]] = relationship(back_populates="base_country")

class Producer(Base):
    __tablename__ = "dim_producers"

    producer_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country_code: Mapped[str | None] = mapped_column(ForeignKey("dim_countries.country_code"))

    base_country: Mapped[Country | None] = relationship(back_populates="producers")

class IngrType(Base):
    __tablename__ = "dim_ingr_types"

    ingr_type: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class Shop(Base):
    __tablename__ = "dim_shops"

    shop_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    start_url: Mapped[str]


class Ingredient(Base):
    __tablename__ = "dim_ingredients"

    ingr_id: Mapped[int] = mapped_column(primary_key=True)
    ingr_type = mapped_column(ForeignKey("dim_ingr_types.ingr_type"))
    name: Mapped[str]
    producer_id = mapped_column(ForeignKey("dim_producers.producer_id"))
    country_code: Mapped[str | None] = mapped_column(ForeignKey("dim_countries.country_code"))
    short_descr: Mapped[str]
    full_descr: Mapped[str | None] = mapped_column(deferred = True)

    category: Mapped[IngrType] = relationship()
    producer: Mapped[Producer] = relationship()
    country: Mapped[Country] = relationship()

    parser_names: Mapped[list[IngredientMapping]] = relationship(back_populates="master_ingredient")

class Malt_Characteristics(Base):
    __tablename__ = "dim_malt_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    color_ebc_min: Mapped[float | None]
    color_ebc_max: Mapped[float | None]
    share_min: Mapped[float | None]
    share_max: Mapped[float | None]
    extract_min: Mapped[float | None]
    extract_max: Mapped[float | None]
    protein_min: Mapped[float | None]
    protein_max: Mapped[float | None]
    kolbach_min: Mapped[float | None]
    kolbach_max: Mapped[float | None]
    diastatic: Mapped[bool | None] = mapped_column(insert_default=False)

    ref_ingr: Mapped[Ingredient] = relationship()

class Hop_Characteristics(Base):
    __tablename__ = "dim_hop_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    alpha_min: Mapped[float | None]
    alpha_max: Mapped[float | None]
    beta_min: Mapped[float | None]
    beta_max: Mapped[float | None]
    cohumulon_min: Mapped[float | None]
    cohumulon_max: Mapped[float | None]
    oils_min: Mapped[float | None]
    oils_max: Mapped[float | None]

    ref_ingr: Mapped[Ingredient] = relationship()

class Yeast_Characteristics(Base):
    __tablename__ = "dim_yeast_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    attenuation_min: Mapped[float | None]
    attenuation_max: Mapped[float | None]
    flocculation: Mapped[str | None]
    ferment_temp_min: Mapped[float | None]
    ferment_temp_max: Mapped[float | None]
    alco_tolerance_min: Mapped[float | None]
    alco_tolerance_max: Mapped[float | None]
    diastatic: Mapped[str | None] = mapped_column(insert_default=False)
    fenolic: Mapped[str | None] = mapped_column(insert_default=False)

    ref_ingr: Mapped[Ingredient] = relationship()

class IngredientMapping(Base):
    __tablename__ = "dim_ingredient_mapping"
    __table_args__ = (UniqueConstraint("ingr_id", "parser_name", name="uq_ingr_parser_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"))
    parser_name: Mapped[str] = mapped_column()

    master_ingredient: Mapped[Ingredient] = relationship(back_populates="parser_names")

class User(Base):
    __tablename__ = "dim_users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    public_id: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str]
    email: Mapped[str]
    hashed_password: Mapped[str]
    disabled: Mapped[bool] = mapped_column(insert_default=False)