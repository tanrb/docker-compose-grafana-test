from fastapi import FastAPI
import requests

app = FastAPI()

## A will get update
## B will validate the update and update the db and return 200 ok 

@app.get("/hello")
async def hello():
    # use internal docker network to communicate with service_b (port 80 exposed)
    response = requests.get("http://service_b:80/")
    return response.json()

@app.get("/")
async def create():
    return {"message": "Hello World from A"}