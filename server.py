from fastapi import FastAPI
from fastapi.responses import FileResponse # To serve frontend file

import psycopg # Postgres database adapter
from pydantic import BaseModel

app = FastAPI()

# 1. Non-dockerized FastAPI and non-dockerized Postgres
# database_uri = "postgres://luke@localhost:5432/notesdb"

# 2. Dockerized FastAPI and non-dockerized Postgres
# Uses special host name that acts as the host's IP
# database_uri = "postgres://luke@host.docker.internal:5432/notesdb"

# 3. Non-dockerized FastAPI and dockerized Postgres
# Uses special host name that acts as the host's IP
database_uri = "postgres://postgres:password@localhost:5432/notesdb"

class Note(BaseModel): # Note schema
    message : str

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