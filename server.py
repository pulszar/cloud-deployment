from fastapi import FastAPI
from fastapi.responses import FileResponse # To serve frontend file

app = FastAPI()

@app.get("/")
def main():
    return FileResponse("index.html")

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}