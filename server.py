from fastapi import FastAPI
from fastapi.responses import FileResponse # To serve frontend file

app = FastAPI()

@app.get("/")
def main():
    return FileResponse("index.html")