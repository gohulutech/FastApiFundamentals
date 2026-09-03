from fastapi_fundamentals.schemas import Car, CarInput, CarOutput, Trip, TripInput, User
from typing import Annotated
from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select
from fastapi_fundamentals.db import get_session
from fastapi_fundamentals.routers.auth import get_current_user

router = APIRouter(prefix="/api/cars")


@router.get("/")
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


@router.get("/{id}")
def car_by_id(session: Annotated[Session, Depends(get_session)], id: int) -> CarOutput:
    car = session.get(Car, id)
    if car:
        return car
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@router.post("/")
def add_car(
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[User, Depends(get_current_user)],
    car_input: CarInput,
) -> Car:
    new_car = Car.model_validate(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@router.delete("/{id}", status_code=204)
def remove_car(session: Annotated[Session, Depends(get_session)], id: int) -> None:
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
        return
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@router.put("/{id}")
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
        session.refresh(car)
        return car
    raise HTTPException(status_code=404, detail=f"No car with id={id}.")


class BadTripException(Exception):
    pass


@router.post("/{car_id}/trips")
def add_trip(
    session: Annotated[Session, Depends(get_session)],
    car_id: int,
    trip_input: TripInput,
) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.model_validate(trip_input, update={"car_id": car_id})
        if new_trip.end < new_trip.start:
            raise BadTripException("Trip end before start")
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")
