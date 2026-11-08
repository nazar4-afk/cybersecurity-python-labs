from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from labs.lab03 import config

Status = Literal["new", "in_progress", "done"]


class CategoryCreate(BaseModel):
    """Модель для створення категорії."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=2, max_length=40, description="Назва категорії")


class CategoryRead(CategoryCreate):
    """Модель для читання категорії."""

    id: int


class RecordCreate(BaseModel):
    """Модель для створення запису."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    code: str = Field(min_length=3, max_length=40, description="Унікальний код запису")
    title: str = Field(min_length=3, max_length=120, description="Назва запису")
    category_id: int = Field(gt=0, description="ID категорії (має бути > 0)")
    value: float = Field(
        ge=config.VALUE_MIN,
        le=config.VALUE_MAX,
        allow_inf_nan=False,
        description="Завантаження каналу у відсотках, від 0 до 100",
    )
    status: Status = Field(description="Статус перевірки вимірювання")


class RecordReplace(RecordCreate):
    """Модель для повної заміни змінюваних полів запису (PUT)."""


class RecordRead(RecordCreate):
    """Модель для читання запису."""

    id: int
    category_name: str


RecordBulk = Annotated[list[RecordCreate], Field(min_length=1, max_length=100)]
