# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

## Diagram

```mermaid
    swimlane-beta TB
        subgraph App
            Docker[Docker]
            db[(PostgresSQL DB)]
            FastAPI[FastAPI Web Server]
        end

        subgraph CD
            GitHub[GitHub Actions]
            cd_event[Push to main]
            Ansible[Ansible]
        end

        subgraph Cloud
            tf[Terraform]
            public_ip[Public IP]
            vnet[VNet]
            subnet[Subnet]
            nic[Network Interface]
            nsg[Network Security Group]
            vm[Ubuntu VM]
        end

        Docker --> FastAPI
        Docker --> db

        GitHub --> cd_event
        cd_event --> Ansible

        tf --> vnet
        vnet --> subnet
        subnet --> nsg
        nsg --> nic
        public_ip --> nic
        nic --> vm
```

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

2. Initialize Terraform
```bash
terraform init
```
3. Plan and review what resources will be spun up
```
terraform plan
```
4. Spin up resources
```bash
terraform apply
```
5. The public IP will output once finished. The app will be available at that IP.
6. Destroy the resources once done with the app
```bash
terraform destroy
```

### Local - Docker (Preferred)

#### Docker Compose (Preferred)

1. Compose the containers

```bash
docker compose up
```

Greeter and notes app will be available at `localhost:8000`

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

#### Non-Dockerized FastAPI and Dockerized Postgres DB

1. In `server.py`, comment out all `database_uri` except for **#3**

2. Run the Postgres container from the image `postgres:17`
```bash
docker run --name deployment-postgres -p 5432:5432 -e "POSTGRES_PASSWORD=password" -e "POSTGRES_DB=notesdb" postgres:17
```
*Include the `-v postgres_vol:/var/lib/postgresql/data` tag if you don't want data loss after destroying the container*

### Local - Non-Docker

1. In `server.py`, comment out all `database_uri` except for **#1**

2. Change the user in the `database_uri` from `luke` to the username of your machine

3. Boot up the server

```bash
uvicorn server:app --port 8000
```
Greeter and notes app will be available at `localhost:8000`



