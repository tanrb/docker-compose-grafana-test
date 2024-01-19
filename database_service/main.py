from fastapi import FastAPI, Request
from pymongo import MongoClient
from bson import json_util
import json
# import logging 
# from multiprocessing import Queue
# from logging_loki import LokiQueueHandler

app = FastAPI()

# loki_logs_handler = LokiQueueHandler(
#     Queue(-1),
#     url='http://gateway:3100/loki/api/v1/push',
#     tags={"application": "fastapi"},
#     version="1",
# )

# uvicorn_access_logger = logging.getLogger("uvicorn.access")
# uvicorn_access_logger.addHandler(loki_logs_handler)

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