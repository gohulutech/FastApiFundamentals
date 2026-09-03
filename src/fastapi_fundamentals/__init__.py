"""FastAPI car-sharing fundamentals package."""

import uvicorn


def main() -> None:
    """Run the FastAPI application with uvicorn.

    Entry point for the ``fastapi-fundamentals`` console script.
    """
    uvicorn.run("fastapi_fundamentals.carsharing:app", reload=True)
