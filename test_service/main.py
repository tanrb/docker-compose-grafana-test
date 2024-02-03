from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pymongo import MongoClient
import requests
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


# Set up logger
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# format_str = '%(levelname)s:%(lineno)s:%(message)s'
# formatter = logging.Formatter(format_str)
# ch.setFormatter(formatter)
# logger.addHandler(ch)
# logger.info('Logger ready')


# OTEL_EXPORTER_OTLP_ENDPOINT="http://otelcol:4137/v1/traces"
# OTEL_RESOURCE_ATTRIBUTES="service.name=auth-service"


# Sets the global default tracer provider


# Creates a tracer from the global tracer provider



# resource = Resource(attributes={
#     SERVICE_NAME: OTEL_RESOURCE_ATTRIBUTES
# })

# traceProvider = TracerProvider(resource=resource)
# processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT))
# traceProvider.add_span_processor(processor)
# trace.set_tracer_provider(traceProvider) #By associating a resource with the tracer provider, additional contextual information about the service or entity that is generating traces is provided
# tracer = trace.get_tracer("__name__")
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
    body = await request.json()
    username = body["username"]
    hash = body["hash"]
    
    user_data = {
        "username": username,
        "hash": hash
    }
    
    # Send the hashed username and password to the auth service
    response = requests.post("http://test1_service:80/authenticate", json=user_data)
    
    return response.json()
    