# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

Early development.

## Prerequisites

### Local

Dependencies in `requirements.txt`

## Usage (MacOS Commands)

### Local

Boot up the server

```bash
uvicorn server:app --port 8000
```
Then go to `localhost:8000`

### Notes

Create the notes Postgres database

```bash
brew services start postgres
createdb notesdb
psql notesdb
```

Create the table

```SQL
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL
);
```


### Docker (preferred)
Build the image from the Dockerfile
```bash
docker build -t cloud-deployment .                
```
Run the image
```bash
docker run  --name cloud-deployment-container -p 8000:8000 cloud-deployment
```