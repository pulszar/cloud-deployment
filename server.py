from fastapi import FastAPI
from fastapi.responses import FileResponse # To serve frontend file

import psycopg # Postgres database adapter
from pydantic import BaseModel

import os

app = FastAPI()

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

class Note(BaseModel): # Note schema
    message : str
    
class TableName(BaseModel): # Note schema
    table_name : str

# Serve frontend
@app.get("/")
def main():
    return FileResponse("index.html")

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.post("/notes")
def send_note(note : Note):
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO notes (note) VALUES (%s) RETURNING id", (note.message,))
            return cursor.fetchone()
        
@app.get("/notes")
def get_notes():
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM notes")
            return cursor.fetchall()
        
@app.post("/initiate")
def initiate_notes():
    with psycopg.connect(database_uri) as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE notes ( id SERIAL PRIMARY KEY, note TEXT NOT NULL)")
            return {"table_status": "created"}