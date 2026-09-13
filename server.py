from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import FileResponse # To serve frontend file
from fastapi.staticfiles import StaticFiles


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
                # Main grocery list
                cursor.execute("CREATE TABLE notes ( id SERIAL PRIMARY KEY, note TEXT NOT NULL)") 
                # Purchase list used to create recommendations
                cursor.execute("CREATE TABLE purchases ( item TEXT NOT NULL PRIMARY KEY, date_purchased TIMESTAMP)")
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
        