"""Unit tests for the SQLModel schemas and password helpers."""
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from fastapi_fundamentals.schemas import (
    Car,
    CarInput,
    Trip,
    TripInput,
    User,
    UserInput,
    UserOutput,
)


class TestUserPassword:
    def test_set_password_stores_hash_not_plaintext(self):
        user = User(username="alice")
        user.set_password("secret123")
        assert user.password_hash
        assert user.password_hash != "secret123"
        assert "secret123" not in user.password_hash

    def test_verify_password_correct(self):
        user = User(username="alice")
        user.set_password("correct horse battery staple")
        assert user.verify_password("correct horse battery staple")

    def test_verify_password_incorrect(self):
        user = User(username="alice")
        user.set_password("right-password")
        assert not user.verify_password("wrong-password")

    def test_verify_password_raises_on_unset_hash(self):
        """passlib raises UnknownHashError on an empty hash instead of False."""
        user = User(username="alice")
        with pytest.raises(Exception):
            user.verify_password("anything")


class TestUserSchemas:
    def test_user_output_omits_password_hash(self):
        data = UserOutput(id=1, username="alice")
        payload = data.model_dump()
        assert "password_hash" not in payload
        assert payload == {"id": 1, "username": "alice"}

    def test_user_input_defaults(self):
        data = UserInput()
        assert data.username is None
        assert data.password == ""


class TestCarSchemas:
    def test_car_input_defaults(self):
        car = CarInput(size="m", doors=5)
        assert car.fuel == "electric"
        assert car.transmission == "auto"

    def test_car_input_requires_size_and_doors(self):
        with pytest.raises(ValidationError):
            CarInput(size="m")

    def test_car_input_validation(self):
        data = CarInput.model_validate(
            {"size": "m", "doors": 5, "transmission": "manual", "fuel": "hybrid"}
        )
        assert data.transmission == "manual"
        assert data.fuel == "hybrid"


class TestTripSchemas:
    def test_trip_input_requires_all_fields(self):
        with pytest.raises(ValidationError):
            TripInput(start=datetime.now())

    def test_trip_validation(self):
        start = datetime.now()
        end = start + timedelta(hours=1)
        trip = TripInput.model_validate(
            {"start": start.isoformat(), "end": end.isoformat(), "distance": 100}
        )
        assert trip.distance == 100

    def test_trip_is_table_model(self):
        # Trip maps to a DB table; Car is its related table object.
        assert Trip.__tablename__ is not None
        assert Car.__tablename__ == "car"
