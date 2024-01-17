from fastapi import FastAPI

app = FastAPI()

## A will get update
## B will validate the update and update the db and return 200 ok 

@app.get("/")
async def create():
    return {"message": "Hello World from B"}