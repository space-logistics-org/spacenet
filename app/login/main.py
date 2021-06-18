from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel

from .auth import oauth2_scheme, UserInDB, fake_users_db, User, get_current_active_user, Token, authenticate_user, create_access_token

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# define the application
app = FastAPI(
    title="SpaceNet Login",
    description="Application to login to SpaceNet.",
    version="0.0"
)

# include any application routers
#app.include_router(...)


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}



# mount the static directory
app.mount("/", StaticFiles(directory="app/login/static", html=True), name="static")
