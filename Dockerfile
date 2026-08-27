FROM python:3

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# host on 0.0.0.0 to open all ports on container so host can use port 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]