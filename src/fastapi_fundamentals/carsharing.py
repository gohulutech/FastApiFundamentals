import uvicorn
from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from fastapi_fundamentals.db import engine
from fastapi_fundamentals.routers import cars


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Car Sharing", lifespan=lifespan)
app.include_router(cars.router)

if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
