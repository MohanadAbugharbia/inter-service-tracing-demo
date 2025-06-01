from fastapi import Response

from src.trace import generate_trace_header


def add_trace_header(
    response: Response,
) -> None:
    response.headers["server-timing"] = generate_trace_header()
