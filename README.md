# Cloud Deployment

A simple FastAPI + Postgres web app deployed on an Azure VM via Terraform and Docker.

The app itself greets a name that is entered and a notes app.

Early development.

## Usage
Boot up the server

```bash
uvicorn server:app --port 8000
```
Then go to `localhost:8000`