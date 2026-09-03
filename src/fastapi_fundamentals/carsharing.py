from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import SQLModel, Session, select
from sqlalchemy import create_engine
from contextlib import asynccontextmanager
from fastapi_fundamentals.schemas import (
    Car,
    CarInput,
    CarOutput,
    Trip,
    TripInput,
    TripOutput,
)

engine = create_engine(
    "sqlite:///carsharing.db", connect_args={"check_same_thread": False}, echo=True
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI(title="Car Sharing", lifespan=lifespan)


@app.get("/api/cars")
def get_cars(
    session: Annotated[Session, Depends(get_session)],
    size: str | None = None,
    doors: int | None = None,
) -> list:
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors == doors)
    return session.exec(query).all()


@app.get("/api/cars/{id}")
def car_by_id(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
    car = session.get(Car, id)
    if car:
        return car
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/")
def add_car(
    session: Annotated[Session, Depends(get_session)], car_input: CarInput
) -> Car:
    new_car = Car.model_validate(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@app.delete("/api/cars/{id}", status_code=204)
def remove_car(session: Annotated[Session, Depends(get_session)], id: int) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
        return
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.put("/api/cars/{id}")
def update_car(
    session: Annotated[Session, Depends(get_session)], id: int, new_data: CarInput
) -> Car:
    car = session.get(Car, id)
    if car:
        car.doors = new_data.doors
        car.fuel = new_data.fuel
        car.size = new_data.size
        car.transmission = new_data.transmission
        session.commit()
        return car
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.post("/api/cars/{car_id}/trips")
def add_trip(
    session: Annotated[Session, Depends(get_session)], car_id: int, trip: TripInput
) -> TripOutput:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.model_validate(trip, update={"car_id": car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    raise HTTPException(status_code=404, detail=f"No car with id={car_id}.")


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
