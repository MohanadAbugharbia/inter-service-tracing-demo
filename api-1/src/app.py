from fastapi import FastAPI, Depends, Response, Query
from warnings import warn
from opentelemetry import trace
import json
from .config import config
from .dependencies import add_trace_header
from .trace import setup_tracing
from .metrics import setup_metrics

# Initialize tracing and metrics
setup_tracing()
setup_metrics()

app = FastAPI(
    title=config.application_name,
    description=config.application_name,
    dependencies=[Depends(add_trace_header)],
)
tracer = trace.get_tracer(__name__)

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

import httpx
@app.get(
    "/",
    summary="Root endpoint",
    description="Root endpoint",
)
async def root(
    age: int = Query(default=0, ge=18, le=60, description="Age of the user")
):
    with tracer.start_as_current_span("call_api_2") as span:
        span.set_attribute("age", age)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{config.api_2_base_url}/?age={age}")

                span.set_attribute("api_2_response_code", response.status_code)
                span.set_attribute("api_2_response_text", response.text)
                span.set_attribute("api_2_response_elapsed", response.elapsed.total_seconds())
                span.set_attribute("api_2_response_request_method", response.request.method)
                span.set_attribute("api_2_response_request_url", str(response.request.url.raw))
                span.set_attribute("api_2_response_request_body", response.request.content)
                
                for header, value in response.headers.items():
                    span.set_attribute(f"api_2_response_header_{header}", value)
                for header, value in response.request.headers.items():
                    span.set_attribute(f"api_2_response_request_header_{header}", value)

                response.raise_for_status()
                data = response.json()

                span.set_attribute("api_2_status", data.get("status", "unknown"))
        except httpx.HTTPStatusError as e:
            span.set_attribute("api_2_error", str(e))
            span.set_attribute("api_2_status", "error")
            span.set_status(trace.StatusCode.ERROR, str(e))
            return {
                "status": "error",
                "api_2_status": "error",
                "message": str(e),
            }
        except Exception as e:
            span.set_attribute("api_2_error", str(e))
            span.set_attribute("api_2_status", "error")
            span.set_status(trace.StatusCode.ERROR, str(e))
            return {
                "status": "error",
                "api_2_status": "error",
                "message": str(e),
            }



    return {
        "status": "ok",
        "api_2_status": "ok",
    }
