from fastapi import FastAPI, Request
from pymongo import MongoClient
import requests

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://mongo:27017", username="root", password="example")
db = client["test"]

@app.post("/authenticate")
async def auth(request: Request):
    # Get username from request
    body = await request.json()
    username = body["username"]
    
    # Get hash from database
    user = db.test.find_one({"username": username})
    if (user == None):
        return {"message": "Failure"}
    
    db_hash = user["hash"]
    
    # Calculate hash from whatever the user entered
    hash = body["hash"]
    
    # Compare the two hashes
    if hash == db_hash:
        #return 200 OK
        print("Success")
        return {"message": "Success"}
    else:
        #return 401 Unauthorized
        print("Failure")
        return {"message": "Failure"}