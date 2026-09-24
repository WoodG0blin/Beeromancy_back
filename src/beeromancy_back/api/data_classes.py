
from pydantic import BaseModel, ConfigDict, model_validator

from beeromancy_back.database import schema


class Ingredient_Response(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingr_id: int
    name: str
    ingr_type: str
    short_descr: str
    producer: str | None
    country: str | None
    full_descr: str | None

    @model_validator(mode="before")
    @classmethod
    def validate_ingredient(cls, v):
        if isinstance(v, schema.Ingredient):
            return {
                "ingr_id": v.ingr_id,
                "name": v.name,
                "ingr_type": v.category.name,
                "short_descr": v.short_descr,
                "producer": v.producer.name if v.producer else None,
                "country": v.country.name if v.country else None,
                "full_descr": v.full_descr if v.full_descr else None
            }
        else:
            raise TypeError("Invalid ingredient data")

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    public_id: str
    username: str
    email: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None