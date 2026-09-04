# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

## Prerequisites

### Deploying on an Azure VM via Terraform

1. Terraform

1. Authentication between Terraform and Azure

Follow Microsoft's guide to [Authenticate Terraform to Azure](https://learn.microsoft.com/en-us/azure/developer/terraform/authenticate-to-azure?tabs=bash)


### Locally without Docker

1. Python 3

1. Packages within `requirements.txt`

Install with `pip install -r requirements.txt`

### Locally with Docker

1. Docker

## Usage

Clone the repo
```bash
git clone https://github.com/pulszar/cloud-deployment.git
```

### Azure VM

1. Change to `/terraform` directory

1. Initialize Terraform
```bash
terraform init
```
1. Plan and review what resources will be spun up
```
terraform plan
```
1. Spin up resources
```bash
terraform apply
```
1. The public IP will output once finished. The app will be available at that IP.
1. Destroy the resources once done with the app
```bash
terraform destroy
```

### Local - Docker (Preferred)

#### Docker Compose (Preferred)

1. Compose the containers

```bash
docker compose up
```

Greeter is available at `localhost:8000`

2. Figure out what the container id is for Postgres
```bash
docker ps
```

3. Enter the containers instance of Postgres to configure it
```bash
docker exec -it {Postgres Container ID} psql -U postgres -d notesdb
```

4. Create table

```SQL
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL
);
```

5. Send a note

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
*Include the `-v postgres_vol:/var/lib/postgresql/data` tag if you don't want data loss after destroying the container*

3. Enter the containers instance of Postgres to configure it
```bash
docker exec -it deployment-postgres psql -U postgres -d notesdb
```

4. Create table

```SQL
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL
);
```

5. Boot up the server

```bash
uvicorn server:app --port 8000
```
6. Go to `localhost:8000`

### Local - Non-Docker

1. In `server.py`, comment out all `database_uri` except for **#1**

2. Change the user in the `database_uri` from `luke` to the username of your machine

3. Boot up the server

```bash
uvicorn server:app --port 8000
```
4. Go to `localhost:8000`

#### Notes Database and Table Configuration

1. Create database

```bash
brew services start postgres
createdb notesdb
psql notesdb
```

2. Create table

```SQL
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    note TEXT NOT NULL
);
```

3. Send a note

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



