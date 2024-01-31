from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import requests
import hashlib

from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace, propagators, baggage
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
from opentelemetry.baggage.propagation import W3CBaggagePropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

import logging

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.name")


OTEL_EXPORTER_OTLP_ENDPOINT="http://otelcol:4137/v1/traces"
OTEL_RESOURCE_ATTRIBUTES="service.name=homepage-service"

resource = Resource(attributes={
    SERVICE_NAME: OTEL_RESOURCE_ATTRIBUTES
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT))
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider)

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
format_str = '%(levelname)s:%(lineno)s:%(message)s'
formatter = logging.Formatter(format_str)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('Logger ready')

app = FastAPI()

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/hello")
async def hello():
    # use internal docker network to communicate with auth_service container (port 80 exposed)
    response = requests.get("http://auth_service:80/")
    return response.json()


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)): ## form object is required
    # Hash the username and password
    with tracer.start_as_current_span("login_homepage") as span:
        ctx = baggage.set_baggage("flow", "login_user")
        headers = {}
        W3CBaggagePropagator().inject(headers, ctx)
        TraceContextTextMapPropagator().inject(headers, ctx)
        logger.info(headers)

        hash = await hash_username_password(username, password)
        
        user_data = {
            "username": username,
            "hash": hash
        }
        current_span = trace.get_current_span()
        # logger.info(current_span)
        # Send the hashed username and password to the auth service
        response = requests.post("http://auth_service:80/authenticate", json=user_data, headers = headers)
        if response == {'message': 'Failure'}:
            span.add_event("log", {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": username,
            })
            return {"message": "Failure"}
        # logger.info(current_span)
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
