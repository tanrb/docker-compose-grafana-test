from fastapi import FastAPI, Request
from pymongo import MongoClient
import requests
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# MongoDB connection
client = MongoClient("mongodb://mongo:27017", username="root", password="example")
db = client["test"]

@app.get("/")
async def hello():
    # use internal docker network to communicate with auth_service container (port 80 exposed)
    return "Hi from auth_service"

@app.post("/authenticate")
async def auth(request: Request):
    # Get username from request
    body = await request.json()
    username = body["username"]
    
    # Get hash from database
    user = db.test.find_one({"username": username})
    
    # If user does not exist, just return failure
    if (user == None):
        return {"message": "Failure"}
    
    db_hash = user["hash"]
    
    # Calculate hash from whatever the user entered
    hash = body["hash"]
    
    # Compare the two hashes
    if hash == db_hash:
        #return 200 OK
        return {"message": "Success"}
    else:
        #return 401 Unauthorized
        return {"message": "Failure"}