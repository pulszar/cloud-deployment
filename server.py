from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse # To serve frontend file
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv

load_dotenv(override=False)

# AUTH
from typing import Annotated
from pwdlib import PasswordHash
import jwt

import statistics
from datetime import datetime, timezone, timedelta


import psycopg # Postgres database adapter
from pydantic import BaseModel

import os

# 1. Non-dockerized FastAPI and non-dockerized Postgres
# database_uri = "postgres://luke@localhost:5432/notesdb"

# 2. Dockerized FastAPI and non-dockerized Postgres
# Uses special host name that acts as the host's IP
# database_uri = "postgres://luke@host.docker.internal:5432/notesdb"

# 3. Non-dockerized FastAPI and dockerized Postgres
# Uses special host name that acts as the host's IP
# database_uri = "postgres://postgres:password@localhost:5432/notesdb"

# 4. Fully dockerized (Docker compose)
# Uses the URI created within the compose yaml
database_uri = os.environ['DATABASE_URI']

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database with notes table
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            try:
                # User table
                cursor.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY, username TEXT NOT NULL, email TEXT NOT NULL, hashed_password TEXT NOT NULL, disabled boolean)") 
                # Main grocery list
                cursor.execute("CREATE TABLE notes ( id SERIAL PRIMARY KEY, note TEXT NOT NULL)") 
                # Purchase list used to create recommendations
                cursor.execute("CREATE TABLE purchases ( item TEXT NOT NULL, date_purchased TIMESTAMP)")
            except Exception:
                pass
    yield # Specify what to do on shutdown after yield

app = FastAPI(lifespan=lifespan)
# app = FastAPI()

class Note(BaseModel): # Note schema
    message : str
    
class Purchase(BaseModel):
    item : str
    date_purchased : str
    
# AUTH

class Token(BaseModel):
    access_token: str
    token_type: str
    
class User(BaseModel):
    user_id: int
    username: str
    email: str
    disabled: str | None = None
    
class UserInDB(User):
    hashed_password: str

app.frontend("/", directory="./frontend")

@app.post("/notes")
def send_note(note : Note):
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO notes (note) VALUES (%s) RETURNING id", (note.message,))
            # return cursor.fetchone()
        
@app.get("/notes")
def get_notes():
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM notes")
            return cursor.fetchall()
        
@app.delete("/grocerylist/{id}")
def delete_grocery_list_item(id : int):
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE (%(int)s)=id", {'int': id})
            
@app.post("/purchase")
def purchse_item(purchase : Purchase):
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO purchases (item, date_purchased) 
                           VALUES (%s, %s);
                           """, 
                           (purchase.item, purchase.date_purchased))

@app.get("/purchase")
def read_purchases():
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM purchases")
            return cursor.fetchall()
        
@app.get("/recommendations")
def get_recommendations():
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            # Get all unique purchases
            cursor.execute("SELECT DISTINCT on (item) item from purchases")
            unique = cursor.fetchall()
            
            recommendations = []
            
            for item in unique:
                current_item_name = item[0]
                # Get all the times this item was purchased
                cursor.execute("SELECT * FROM purchases WHERE item=(%s)", (current_item_name,))
                all_purchases_for_item = cursor.fetchall()
                
                # There must be at least 2 purchases of a product to make a recommendation. Skip if less than 2
                if len(all_purchases_for_item) < 2:
                    continue
                
                # For this item, get all purchase gaps
                gaps_between_purchases = []
                for p in range(len(all_purchases_for_item)):
                     # If on last item, don't try and calculate a new range
                    if p + 1 >= len(all_purchases_for_item):
                        break
                    
                    purchase_gap = all_purchases_for_item[p + 1][1] - all_purchases_for_item[p][1]
                    gaps_between_purchases.append(purchase_gap.total_seconds()) # Purchase timestamp
                
                # Core recommendation logic
                # If the time since last purchase is longer than usual, recommend the item
                
                current_time_utc = datetime.now(timezone.utc)
                last_time_purchased_utc = all_purchases_for_item[p][-1].replace(tzinfo=timezone.utc)
                
                seconds_since_last_purchase = (current_time_utc - last_time_purchased_utc).total_seconds()
                average_seconds_between_purchases = statistics.mean(gaps_between_purchases)
                
                if seconds_since_last_purchase > average_seconds_between_purchases:
                    attributes = {}
                    
                    attributes["recommendation"] = current_item_name
                    attributes["last_purchased"] = all_purchases_for_item[p][-1]
                    attributes["average_seconds_between_purchases"] = average_seconds_between_purchases
                    recommendations.append(attributes)
                    
            return recommendations
        
# AUTHENTICATION #

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash('dummypassword')

TOKEN_EXPIRE_INTERVAL_MINUTES = 30

SECRET_KEY = os.environ['GROCERY_SECRET_KEY']
ALGORITHM = "HS256"

def get_user(username : str) -> UserInDB:
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=(%s)", (username,))
            
            user_result = cursor.fetchone()
            if len(user_result) > 0:
                return UserInDB(
                    user_id=user_result[0],
                    username=user_result[1],
                    email=user_result[2],
                    hashed_password=user_result[3],
                    disabled=user_result[4]
                )
                
def verify_password(password: str, password_hash: str):
    return password_hash.verify(password, password_hash)

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if verify_password(password, user.hashed_password):
        return user
    
def get_access_token(data: dict, token_expire_interval: timedelta):
    to_encode = data.copy()
    if token_expire_interval:
        exp = datetime.now(timezone.utc) + token_expire_interval
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.get(exp)
    token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return token
    

@app.post('/token')
async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(login_form.username, login_form.password)
    if not user:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token_expire_interval = timedelta(minutes=TOKEN_EXPIRE_INTERVAL_MINUTES)
    token = get_access_token( 
                data={ "sub": user.username, "id": user.user_id }, 
                token_expire_interval=token_expire_interval
            )
    