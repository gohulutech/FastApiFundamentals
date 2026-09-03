from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, Request, status
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from fastapi_fundamentals.db import engine
from fastapi_fundamentals.routers import cars, web


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Car Sharing", lifespan=lifespan)
app.include_router(cars.router)
app.include_router(web.router)


@app.exception_handler(cars.BadTripException)
async def unicorn_exception_handler(request: Request, exc: cars.BadTripException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"message": "Bad Trip"},
    )


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
