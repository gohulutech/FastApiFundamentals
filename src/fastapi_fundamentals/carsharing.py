import uvicorn
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from fastapi_fundamentals.db import engine
from fastapi_fundamentals.routers import cars, web, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Car Sharing", lifespan=lifespan)
app.include_router(cars.router)
app.include_router(web.router)
app.include_router(auth.router)

origins = ["http://localhost:8000", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(cars.BadTripException)
async def unicorn_exception_handler(request: Request, exc: cars.BadTripException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"message": "Bad Trip"},
    )


@app.middleware("http")
async def add_cars_cookie(request: Request, call_next):
    response = await call_next(request)
    response.set_cookie(key="cars_cookie", value="you_visited_the_carsharing_app")
    return response


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
