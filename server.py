from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse # To serve frontend file
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError

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

password_hash = PasswordHash.recommended()
            
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database with notes table
    admin_hashed_password = password_hash.hash(os.environ['ADMIN_PASSWORD'])
    
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            # Create tables
            try:
                # User table
                cursor.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY, username TEXT NOT NULL, email TEXT NOT NULL, hashed_password TEXT NOT NULL, disabled boolean)") 
                cursor.execute("""
                            INSERT INTO users (username, email, hashed_password, disabled)
                            VALUES (%s, %s, %s, %s);
                            """, (os.environ['ADMIN_USERNAME'], os.environ['ADMIN_EMAIL'], admin_hashed_password, False)
                            )
            except Exception:
                pass
            
            try: 
                # Main grocery list
                cursor.execute("CREATE TABLE notes ( id SERIAL PRIMARY KEY, note TEXT NOT NULL)") 
            except Exception:
                pass
            
            try:
                # Purchase list used to create recommendations
                cursor.execute("CREATE TABLE purchases ( item TEXT NOT NULL, date_purchased TIMESTAMP)")
            except Exception:
                pass
            
    # with psycopg.connect(database_uri) as connection:
    #     with connection.cursor() as cursor:
    #         cursor.execute("SELECT username FROM users WHERE username=(%s)", (os.environ['ADMIN_USERNAME'],))
    #         result = cursor.fetchone()
    #         if result == None:
    #             admin_found = False
    #         admin_found = True
            
    # if not admin_found:
    #     hashed_password = password_hash.hash(os.environ['ADMIN_PASSWORD'])
    #     with psycopg.connect(database_uri) as connection:
    #         with connection.cursor() as cursor:
    #             cursor.execute("""
    #                         INSERT INTO users (username, email, disabled, hashed_password)
    #                         VALUES (%s, %s, %s, %s);
    #                         """, ('test', 
    #                                 'test', 
    #                                 'test', 
    #                                 'test',)
    #                         )
        
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
    disabled: bool | None = None
    
class UserInDB(User):
    hashed_password: str
    
class TokenData(BaseModel):
    username : str

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

DUMMY_HASH = password_hash.hash('dummypassword')

TOKEN_EXPIRE_INTERVAL_MINUTES = 30

SECRET_KEY = os.environ['GROCERY_SECRET_KEY']
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]) -> User:
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    credentials_exception = HTTPException (
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        username = decoded_token.get("sub")
        user = get_user(username)
    except InvalidTokenError:
        raise credentials_exception
    if not user:
        raise credentials_exception
    return user

def get_current_active_user(current_active_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_active_user.disabled:
        raise HTTPException (
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account disabled"
        )
    return current_active_user
    

def get_user(username : str) -> UserInDB:
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=(%s)", (username,))
            
            user_result = cursor.fetchone()
            
            if user_result:
                return UserInDB(
                    user_id=int(user_result[0]),
                    username=user_result[1],
                    email=user_result[2],
                    hashed_password=user_result[3],
                    disabled=user_result[4]
                )
                
def verify_password(password: str, password_hash_input: str):
    return password_hash.verify(password, password_hash_input)

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
    return Token(access_token=token, token_type="bearer")
  
@app.get('/users/me')  
def get_current_user_api(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
    return current_user