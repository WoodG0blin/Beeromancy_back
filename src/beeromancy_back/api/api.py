import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from beeromancy_back.database import DatabaseController, schema

from .data_classes import Ingredient_Response, Token, UserCreate, UserResponse
from .security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI()

@app.get("/ingredients/{ingr_id}", response_model=Ingredient_Response)
def get_ingredient(ingr_id: int):
    with DatabaseController() as db:
        ingredient = db.get_ingredient_by_id(ingr_id)
        if ingredient is None:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        result = Ingredient_Response.model_validate(ingredient)
    return result

@app.get("/ingredients/{ingr_type}/all", response_model=list[Ingredient_Response])
def get_ingredients_by_type(ingr_type: str):
    with DatabaseController() as db:
        ingredients = [Ingredient_Response.model_validate(ingredient) for ingredient in db.get_ingredients_by_type(ingr_type)]
    return ingredients

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with DatabaseController() as db:
        user = db.get_user_by_username(form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/me", response_model=UserResponse)
def read_user_me(username: str = Depends(decode_access_token)):
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    with DatabaseController() as db:
        user = db.get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        elif user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        result = UserResponse.model_validate(user)
    return result

@app.post("/register", response_model=UserResponse)
def register_user(user_create: UserCreate):
    with DatabaseController() as db:
        existing_user = db.get_user_by_username(user_create.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = hash_password(user_create.password)
        new_user = schema.User(
            public_id=str(uuid.uuid4()),
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            disabled=False
        )
        db.session.add(new_user)
        db.session.commit()

        result = UserResponse.model_validate(new_user)

    return result
