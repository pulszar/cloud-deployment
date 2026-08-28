# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

Early development.

## Prerequisites

### Local

Dependencies in `requirements.txt`

## Usage

### Local

Boot up the server

```bash
uvicorn server:app --port 8000
```
Then go to `localhost:8000`

### Notes

#### Create Database

```bash
brew services start postgres
createdb notesdb
psql notesdb
```

#### Create Table

```SQL
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL
);
```

#### Send a Note

Go to `localhost:8000/docs`,  select the `POST /notes` endpoint, and fill in the value for `message`.

You can also make the following `curl` request:

```bash
curl -X 'POST' \
  'http://localhost:8000/notes' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Your note"
}'
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