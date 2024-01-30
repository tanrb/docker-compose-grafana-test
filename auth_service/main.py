from fastapi import FastAPI, Request
from pymongo import MongoClient
import requests
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler 
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, SimpleLogRecordProcessor, ConsoleLogExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry._logs import (
    SeverityNumber,
    get_logger,
    get_logger_provider,
    std_to_otel,
    set_logger_provider
)

DEBUG_LOG_OTEL_TO_PROVIDER = True
DEBUG_LOG_OTEL_TO_CONSOLE  = True
def otel_trace_init():
    trace.set_tracer_provider(
       TracerProvider(
           resource=Resource.create({}),
       ),
    )
    if DEBUG_LOG_OTEL_TO_PROVIDER:
        otel_endpoint_url, otel_http_headers = "otelcol:4138",{}
        otlp_span_exporter = OTLPSpanExporter(endpoint=otel_endpoint_url,headers=otel_http_headers)
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_span_exporter))
    if DEBUG_LOG_OTEL_TO_CONSOLE:
        trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))


otel_trace_init()
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
    
    current_span = trace.get_current_span()

    if current_span:
        current_span.set_attribute("http.method", request.method)
        current_span.set_attribute("http.url", str(request.url))
    body = await request.json()
    username = body["username"]

    # Get hash from database
    user = db.test.find_one({"username": username})

    # If user does not exist, just return failure
    if user is None:
        current_span.set_attribute("authentication.status", "failure")
        return {"message": "Failure"}

    db_hash = user["hash"]

    # Calculate hash from whatever the user entered
    provided_hash = body["hash"]

    # Compare the two hashes
    if provided_hash == db_hash:
        current_span.set_attribute("authentication.status", "success")
        return {"message": "Success"}
    else:
        current_span.set_attribute("authentication.status", "failure")
        return {"message": "Failure"}

