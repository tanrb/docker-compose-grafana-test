from fastapi import FastAPI, Request
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
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
format_str = '%(levelname)s:%(lineno)s:%(message)s'
formatter = logging.Formatter(format_str)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.info('Logger ready')


OTEL_EXPORTER_OTLP_ENDPOINT="http://otelcol:4137/v1/traces"
OTEL_RESOURCE_ATTRIBUTES="service.name=auth-service"


# Sets the global default tracer provider


# Creates a tracer from the global tracer provider



resource = Resource(attributes={
    SERVICE_NAME: OTEL_RESOURCE_ATTRIBUTES
})

traceProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT))
traceProvider.add_span_processor(processor)
trace.set_tracer_provider(traceProvider) #By associating a resource with the tracer provider, additional contextual information about the service or entity that is generating traces is provided
tracer = trace.get_tracer("__name__")
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
    headers = request.headers
    logger.info(f"Received headers: {headers}")
    carrier ={'Traceparent': headers['Traceparent']}
    ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
    logger.info(f"Received context: {ctx}")

    b2 ={'baggage': headers['Baggage']}
    ctx2 = W3CBaggagePropagator().extract(b2, context=ctx)
    logger.info(f"Received context2: {ctx2}")

    with tracer.start_as_current_span("auth-user", context=ctx2) as span:
        
        # Get username from request
        body = await request.json()
        username = body["username"]
        
        # Get hash from database
        user = db.test.find_one({"username": username})
        current_span = trace.get_current_span()
        # logger.info(current_span)
        
        # If user does not exist, just return failures
        if (user == None):
            return {"message": "Failure"}
        
        db_hash = user["hash"]
        
        # Calculate hash from whatever the user entered
        hash = body["hash"]
        
        # logger.info(current_span)
        # Compare the two hashes
        if hash == db_hash:
            #return 200 OK
            return {"message": "Success"}
        else:
            #return 401 Unauthorized
            span.add_event("log", {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": username,
            })
            return {"message": "Failure"}
        

