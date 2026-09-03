from pathlib import Path
from typing import Annotated
from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from fastapi_fundamentals.db import get_session
from fastapi_fundamentals.routers.cars import get_cars

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request, cars_cookie: Annotated[str | None, Cookie()]):
    print(cars_cookie)
    return templates.TemplateResponse(request=request, name="home.html")


@router.post("/search", response_class=HTMLResponse)
def search(
    size: Annotated[str, Form()],
    doors: Annotated[int, Form()],
    request: Request,
    session: Annotated[Session, Depends(get_session)],
):
    cars = get_cars(size=size, doors=doors, session=session)
    return templates.TemplateResponse(
        name="search_results.html", request=request, context={"cars": cars}
    )
