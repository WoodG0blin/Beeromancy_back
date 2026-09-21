from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass

class Country(Base):
    __tablename__ = "dim_countries"

    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str]

    producers: Mapped[List[Producer]] = relationship(back_populates="base_country")

class Producer(Base):
    __tablename__ = "dim_producers"

    producer_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country_code: Mapped[Optional[str]] = mapped_column(ForeignKey("dim_countries.country_code"))

    base_country: Mapped[Optional[Country]] = relationship(back_populates="producers")

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
    country_code: Mapped[Optional[str]] = mapped_column(ForeignKey("dim_countries.country_code"))
    short_descr: Mapped[str]
    full_descr: Mapped[Optional[str]] = mapped_column(deferred = True)

    category: Mapped[IngrType] = relationship()
    producer: Mapped[Producer] = relationship()
    country: Mapped[Country] = relationship()

    parser_names: Mapped[List[IngredientMapping]] = relationship(back_populates="master_ingredient")

class Malt_Characteristics(Base):
    __tablename__ = "dim_malt_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    color_ebc_min: Mapped[Optional[float]]
    color_ebc_max: Mapped[Optional[float]]
    share_min: Mapped[Optional[float]]
    share_max: Mapped[Optional[float]]
    extract_min: Mapped[Optional[float]]
    extract_max: Mapped[Optional[float]]
    protein_min: Mapped[Optional[float]]
    protein_max: Mapped[Optional[float]]
    kolbach_min: Mapped[Optional[float]]
    kolbach_max: Mapped[Optional[float]]
    diastatic: Mapped[Optional[bool]] = mapped_column(insert_default=False)

    ref_ingr: Mapped[Ingredient] = relationship()

class Hop_Characteristics(Base):
    __tablename__ = "dim_hop_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    alpha_min: Mapped[Optional[float]]
    alpha_max: Mapped[Optional[float]]
    beta_min: Mapped[Optional[float]]
    beta_max: Mapped[Optional[float]]
    cohumulon_min: Mapped[Optional[float]]
    cohumulon_max: Mapped[Optional[float]]
    oils_min: Mapped[Optional[float]]
    oils_max: Mapped[Optional[float]]

    ref_ingr: Mapped[Ingredient] = relationship()

class Yeast_Characteristics(Base):
    __tablename__ = "dim_yeast_characteristics"

    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"), primary_key=True)
    attenuation_min: Mapped[Optional[float]]
    attenuation_max: Mapped[Optional[float]]
    flocculation: Mapped[Optional[str]]
    ferment_temp_min: Mapped[Optional[float]]
    ferment_temp_max: Mapped[Optional[float]]
    alco_tolerance_min: Mapped[Optional[float]]
    alco_tolerance_max: Mapped[Optional[float]]
    diastatic: Mapped[Optional[str]] = mapped_column(insert_default=False)
    fenolic: Mapped[Optional[str]] = mapped_column(insert_default=False)

    ref_ingr: Mapped[Ingredient] = relationship()

class IngredientMapping(Base):
    __tablename__ = "dim_ingredient_mapping"
    __table_args__ = (UniqueConstraint("ingr_id", "parser_name", name="uq_ingr_parser_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ingr_id = mapped_column(ForeignKey("dim_ingredients.ingr_id"))
    parser_name: Mapped[str] = mapped_column()

    master_ingredient: Mapped[Ingredient] = relationship(back_populates="parser_names")