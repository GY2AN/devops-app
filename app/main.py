from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.routes.health import router as health_router
import time

app = FastAPI(title="devops-app")
app.include_router(health_router)

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

@app.middleware("http")
async def track_metrics(request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = time.time() - start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.url.path).observe(latency)
    return response

@app.get("/")
def root():
    return {"message": "devops-app is running", "version": "1.0.0"}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
