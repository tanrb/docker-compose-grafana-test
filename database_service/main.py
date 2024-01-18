from fastapi import FastAPI, Request
from pymongo import MongoClient
from bson import json_util
import json

app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb://mongo:27017", username="root", password="example")
db = client["test"]

@app.get("/clear")
async def drop_database():
    db.test.drop()
    return {"message": "Dropped"}

@app.post("/add")
async def add(request: Request):
    body = await request.json()
    
    username = body["username"]
    hash = body["hash"]
    db.test.insert_one({"username": username, "hash": hash})
    
    return {"message": "Added"}

@app.get("/count")
async def count_users():
    return {"count": db.test.count_documents({})}

@app.get("/")
async def list_users():
    users = []
    for user in db.test.find():
        # Convert MongoDB document to a dict
        user_data = json.loads(json_util.dumps(user))
        users.append(user_data)
    return {"users": users}