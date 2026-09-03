"""Unit tests for the /api/cars router: CRUD, filtering, and trips."""
from datetime import datetime, timedelta

from fastapi_fundamentals.schemas import User


def _seed_user(session, username="alice", password="secret123") -> User:
    user = User(username=username)
    user.set_password(password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _auth_headers(username="alice"):
    return {"Authorization": f"Bearer {username}"}


def _seed_car(session, size="m", doors=5, fuel="electric", transmission="auto"):
    from fastapi_fundamentals.schemas import Car

    car = Car(size=size, doors=doors, fuel=fuel, transmission=transmission)
    session.add(car)
    session.commit()
    session.refresh(car)
    return car


class TestGetCars:
    def test_empty_list(self, client):
        response = client.get("/api/cars/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_cars(self, client, session):
        _seed_car(session, size="m", doors=5)
        _seed_car(session, size="l", doors=4)
        response = client.get("/api/cars/")
        assert response.status_code == 200
        cars = response.json()
        assert len(cars) == 2

    def test_filter_by_size(self, client, session):
        _seed_car(session, size="m", doors=5)
        _seed_car(session, size="l", doors=4)
        response = client.get("/api/cars/", params={"size": "m"})
        cars = response.json()
        assert len(cars) == 1
        assert cars[0]["size"] == "m"

    def test_filter_by_doors(self, client, session):
        _seed_car(session, size="m", doors=5)
        _seed_car(session, size="m", doors=3)
        response = client.get("/api/cars/", params={"doors": 3})
        cars = response.json()
        assert len(cars) == 1
        assert cars[0]["doors"] == 3


class TestCarById:
    def test_get_existing_car(self, client, session):
        car = _seed_car(session, size="m", doors=5)
        response = client.get(f"/api/cars/{car.id}")
        assert response.status_code == 200
        assert response.json()["size"] == "m"
        assert response.json()["doors"] == 5

    def test_get_missing_car_404(self, client):
        response = client.get("/api/cars/999")
        assert response.status_code == 404
        assert "999" in response.json()["detail"]


class TestAddCar:
    def test_add_car_requires_auth(self, client):
        response = client.post(
            "/api/cars/",
            json={"size": "m", "doors": 5},
        )
        assert response.status_code == 401

    def test_add_car_success(self, client, session):
        _seed_user(session)
        response = client.post(
            "/api/cars/",
            headers=_auth_headers(),
            json={"size": "m", "doors": 5, "transmission": "manual", "fuel": "hybrid"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["size"] == "m"
        assert body["doors"] == 5
        assert body["transmission"] == "manual"
        assert body["fuel"] == "hybrid"
        assert body["id"] is not None

    def test_add_car_applies_defaults(self, client, session):
        _seed_user(session)
        response = client.post(
            "/api/cars/",
            headers=_auth_headers(),
            json={"size": "s", "doors": 2},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["fuel"] == "electric"
        assert body["transmission"] == "auto"


class TestUpdateCar:
    def test_update_car_success(self, client, session):
        _seed_user(session)
        car = _seed_car(session, size="m", doors=5)
        response = client.put(
            f"/api/cars/{car.id}",
            headers=_auth_headers(),
            json={"size": "l", "doors": 4, "transmission": "auto", "fuel": "diesel"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["size"] == "l"
        assert body["doors"] == 4
        assert body["fuel"] == "diesel"

    def test_update_missing_car_404(self, client, session):
        _seed_user(session)
        response = client.put(
            "/api/cars/999",
            headers=_auth_headers(),
            json={"size": "m", "doors": 5},
        )
        assert response.status_code == 404


class TestDeleteCar:
    def test_delete_car_success(self, client, session):
        _seed_user(session)
        car = _seed_car(session, size="m", doors=5)
        response = client.delete(f"/api/cars/{car.id}", headers=_auth_headers())
        assert response.status_code == 204

    def test_delete_missing_car_404(self, client, session):
        _seed_user(session)
        response = client.delete("/api/cars/999", headers=_auth_headers())
        assert response.status_code == 404


class TestTrips:
    def _add_trip_payload(self):
        start = datetime.now()
        end = start + timedelta(hours=2)
        return {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "distance": 120,
        }

    def test_add_trip_success(self, client, session):
        car = _seed_car(session, size="m", doors=5)
        response = client.post(
            f"/api/cars/{car.id}/trips",
            json=self._add_trip_payload(),
        )
        assert response.status_code == 200
        body = response.json()
        assert body["distance"] == 120
        assert body["car_id"] == car.id

    def test_add_trip_to_missing_car_404(self, client):
        response = client.post(
            "/api/cars/999/trips",
            json=self._add_trip_payload(),
        )
        assert response.status_code == 404

    def test_trip_end_before_start_raises_422(self, client, session):
        car = _seed_car(session, size="m", doors=5)
        start = datetime.now()
        end = start - timedelta(hours=2)
        response = client.post(
            f"/api/cars/{car.id}/trips",
            json={"start": start.isoformat(), "end": end.isoformat(), "distance": 10},
        )
        assert response.status_code == 422
        assert response.json()["message"] == "Bad Trip"
