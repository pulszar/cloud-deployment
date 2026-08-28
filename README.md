# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

Early development.

## Prerequisites

### Local

Dependencies in `requirements.txt` and Postgres for creating the database and table

## Usage

### Docker (preferred)
#### Dockerized FastAPI and Non-Dockerized Postgres DB

1. In `server.py`, comment out all `database_uri` except for **#2**

2. Change the user in the `database_uri` from `luke` to the username of your machine

3. Build the image from the Dockerfile
```bash
docker build -t cloud-deployment .                
```
4. Run the image
```bash
docker run  --name cloud-deployment-container -p 8000:8000 cloud-deployment
```

5. Configure the database by following [Notes Database and Table Configuration](#notes-database-and-table-configuration)

#### Non-Dockerized FastAPI and Dockerized Postgres DB

1. In `server.py`, comment out all `database_uri` except for **#3**

2. Run the Postgres container from the image `postgres:17`
```bash
docker run --name deployment-postgres -p 5432:5432 -e "POSTGRES_PASSWORD=password" -e "POSTGRES_DB=notesdb" postgres:17
```
*Include the `-v postgres_vol:/var/lib/postgres/data` tag if you don't want data loss after destroying the container*

### Local

1. Boot up the server

```bash
uvicorn server:app --port 8000
```
2. Go to `localhost:8000`

### Notes Database and Table Configuration

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



