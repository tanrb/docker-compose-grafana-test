from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

## A will get update
## B will validate the update and update the db and return 200 ok 

# MongoDB connection
client = MongoClient("mongodb://mongo:27017", username="root", password="example")
db = client["test"]

@app.post("/add")
async def add():
    db.test.insert_one({"test": "test"})
    return {"message": "Added"}

@app.get("/")
async def return_count():
    return {"count": db.test.count_documents({})}