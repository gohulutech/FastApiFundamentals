from datetime import datetime
from passlib.context import CryptContext
from sqlmodel import VARCHAR, Column, Relationship, SQLModel, Field

pwd_context = CryptContext(schemes=["bcrypt"])


class UserInput(SQLModel):
    username: str | None = None
    password: str | None = ""


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        sa_column=Column("username", VARCHAR, unique=True, index=True)
    )
    password_hash: str = ""

    def set_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class UserOutput(SQLModel):
    id: int
    username: str


class TripInput(SQLModel):
    start: datetime
    end: datetime
    distance: int


class TripOutput(TripInput):
    id: int


class Trip(TripInput, table=True):
    id: int | None = Field(default=None, primary_key=True)
    car_id: int = Field(foreign_key="car.id")
    car: "Car" = Relationship(back_populates="trips")


class CarInput(SQLModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"size": "m", "doors": 5, "transmission": "manual", "fuel": "hybrid"}
            ]
        }
    }


class Car(CarInput, table=True):
    id: int | None = Field(primary_key=True, default=None)
    trips: list[Trip] = Relationship(back_populates="car")


class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []
