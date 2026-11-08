from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from fastapi import status as http_status

from labs.lab03 import repository, schemas

router = APIRouter(prefix="/categories", tags=["categories"])

CategoryId = Annotated[int, Path(gt=0, description="Ідентифікатор категорії (> 0)")]


@router.post(
    "",
    response_model=schemas.CategoryRead,
    status_code=http_status.HTTP_201_CREATED,
    summary="Створити категорію",
    responses={409: {"description": "Категорія з такою назвою вже існує"}},
)
def create_category(category: schemas.CategoryCreate) -> dict:
    """Створити нову категорію"""
    try:
        return repository.create_category(name=category.name)
    except ValueError as e:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT, detail=str(e)
        ) from e


@router.get(
    "",
    response_model=list[schemas.CategoryRead],
    summary="Отримати список категорій",
)
def list_categories() -> list[dict]:
    """Отримати список всіх категорій"""
    return repository.list_categories()


@router.delete(
    "/{category_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    summary="Видалити категорію",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Категорія містить записи"},
    },
)
def delete_category(category_id: CategoryId) -> None:
    """Видалити порожню категорію"""
    try:
        repository.delete_category(category_id=category_id)
    except ValueError as e:
        if "не знайдена" in str(e):
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND, detail=str(e)
            ) from e
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT, detail=str(e)
        ) from e
