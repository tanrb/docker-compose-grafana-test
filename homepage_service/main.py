from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import requests
import hashlib

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/hello")
async def hello():
    # use internal docker network to communicate with service_b (port 80 exposed)
    response = requests.get("http://auth_service:80/")
    return response.json()


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Hash the username and password
    hash = await hash_username_password(username, password)
    
    user_data = {
        "username": username,
        "hash": hash
    }

    # Send the hashed username and password to the auth service
    response = requests.post("http://auth_service:80/authenticate", json=user_data)
    
    return response.json()
    
# Method to hash username and password
@app.get("/hash")
async def hash_username_password(username, password):
    combined = username + password

    # Create a new SHA256 hash object
    hash_obj = hashlib.sha256()

    # Update the hash object with the bytes of the combined string
    hash_obj.update(combined.encode())

    # Get the hexadecimal representation of the hash
    hash_hex = hash_obj.hexdigest()

    return hash_hex

@app.post("/register")
async def create_user(newUsername: str = Form(...), newPassword: str = Form(...)):
    hash = await hash_username_password(newUsername, newPassword)
    user_data = {
        "username": newUsername,
        "hash": hash
    }
    requests.post("http://database_service:80/add", json=user_data)
    
    return {"added": user_data}

@app.get("/")
async def main():
    return FileResponse("static/index.html")
