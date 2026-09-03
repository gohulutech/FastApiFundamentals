"""Interactive CLI to create a user in the carsharing database."""

import logging
from getpass import getpass

from sqlmodel import Session, SQLModel, create_engine

from fastapi_fundamentals.schemas import User

logging.getLogger("passlib").setLevel(logging.ERROR)

DB_URL = "sqlite:///carsharing.db"


def main() -> None:
    """Prompt for a username/password and persist a new user."""
    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        echo=True,
    )

    print("Creating tables (if necessary)")
    SQLModel.metadata.create_all(engine)
    print("--------")
    print("This script will create a user and save it in the database.")

    username = input("Please enter username\n")
    pwd = getpass("Please enter password\n")

    with Session(engine) as session:
        user = User(username=username)
        user.set_password(pwd)
        session.add(user)
        session.commit()

    print("User created.")
