from fastapi import FastAPI, Depends, Query
from warnings import warn

from .config import config
from .dependencies import add_trace_header
from .trace import setup_tracing
from .metrics import setup_metrics

# Initialize tracing and metrics
tracer = setup_tracing()
meter = setup_metrics()

app = FastAPI(
    title=config.application_name,
    description=config.application_name,
    dependencies=[Depends(add_trace_header)],
)


if config.enable_fastapi_telemetry:
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor().instrument_app(
            app,
            excluded_urls="/health",
        )
    except ImportError:
        warn("FastAPIInstrumentor not installed. Skipping FastAPI instrumentation.")

if config.enable_httpx_telemetry:
    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPXClientInstrumentor().instrument()
    except ImportError:
        warn("HTTPXClientInstrumentor not installed. Skipping HTTPX instrumentation.")


@app.get(
    "/health",
    summary="Health check",
    description="Health check endpoint",
)
def health():
    return {"status": "ok"}

@app.get(
    "/",
    summary="Root endpoint",
    description="Root endpoint",
)
async def root(
    age: int = Query(default=0, ge=18, le=50, description="Age of the user")
) -> dict:
    return {
        "status": "ok",
    }
