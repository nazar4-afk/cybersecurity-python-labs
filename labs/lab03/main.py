from contextlib import asynccontextmanager

from fastapi import FastAPI

from labs.lab03 import config
from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


@asynccontextmanager
async def lifespan(app):
    initialize_database()
    yield


app = FastAPI(
    title="Облік завантаження каналів зв'язку. ",
    description=(
        "Сервіс обліку вимірювань завантаження каналів зв'язку. "
        f"Одиниця вимірювання: {config.UNIT}. "
        f"Поріг високого навантаження: {config.THRESHOLD}%. "
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["service"])
def ping():
    return {"status": "ok"}


@app.get("/student", tags=["service"])
def get_student():
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }
