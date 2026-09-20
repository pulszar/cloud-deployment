from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse # To serve frontend file
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm

# AUTH
from typing import Annotated

import statistics
from datetime import datetime, timezone


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
                cursor.execute("CREATE TABLE users ( id SERIAL PRIMARY KEY, username TEXT NOT NULL, hashed_password TEXT NOT NULL, disabled boolean)") 
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

# def get_user(username : str):
    

# def authenticate_user(username: str, password: str):
#     user = get_user(username)

# @app.post('/token')
# async def login(login_form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
#     user = authenticate_user(login_form.username, login_form.password)