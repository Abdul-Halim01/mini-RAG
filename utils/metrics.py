from prometheus_client import Counter, Histogram, Gauge, CONTENT_TYPE_LATEST
from fastapi import FastAPI,Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=registry
)

# VECTOR_DB_OPERATIONS = Counter(
#     'vector_db_operations_total',
#     'Vector database operations',
#     ['operation', 'status'],
#     registry=registry
# )

# EMBEDDING_GENERATION_LATENCY = Histogram(
#     'embedding_generation_seconds',
#     'Embedding generation latency',
#     ['model', 'status'],
#     registry=registry
# )

class PrometheusMiddleware(BaseHTTPMiddleware):
    def dispatch(self,request: Request,call_next):
        start_time = time.time()
        # Process The Request
        response = await call_next(request)
        # Record The Response
        duration = time.time() - start_time
        endpoint = request.url.path

        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=response.status_code).inc()
        
        return response

    def setup_metrics(app: FastAPI):
        app.add_middleware(PrometheusMiddleware)

        @app.get("/A7kQ9x_T2L_mf3Zp_8_Wq1Rs",include_in_scheme=False)
        def metrics():
            return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)