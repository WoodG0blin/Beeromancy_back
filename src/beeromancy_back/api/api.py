from fastapi import FastAPI

from beeromancy_back.database import DatabaseController

app = FastAPI()

@app.get("/ingredients/{ingr_id}")
def get_ingredient(ingr_id: int):
    with DatabaseController() as db:
        ingredient = db.get_ingredient_by_id(ingr_id)
        if ingredient is None:
            return {"error": "Ingredient not found"}
        return ingredient

@app.get("/ingredients/{ingr_type}/all")
def get_ingredients_by_type(ingr_type: str):
    with DatabaseController() as db:
        ingredients = db.get_ingredients_by_type(ingr_type)
        return ingredients