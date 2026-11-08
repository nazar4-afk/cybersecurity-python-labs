from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from labs.lab03 import config, repository, schemas

router = APIRouter(prefix="/records", tags=["records"])

RecordId = Annotated[int, Path(gt=0, description="Ідентифікатор запису (> 0)")]


def _error_to_http(error: ValueError) -> HTTPException:
    """Перетворити помилку repository на HTTP-помилку 404 або 409."""
    err = str(error)
    if "не знайдена" in err:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
    if "Дублікат" in err:
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=err)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)


@router.post(
    "",
    response_model=schemas.RecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Створити запис",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Дублікат code"},
    },
)
def create_record(record: schemas.RecordCreate) -> dict:
    """Створити новий запис"""
    try:
        return repository.create_record(
            code=record.code,
            title=record.title,
            category_id=record.category_id,
            value=record.value,
            status=record.status,
        )
    except ValueError as e:
        raise _error_to_http(e) from e


@router.post(
    "/bulk",
    response_model=list[schemas.RecordRead],
    status_code=status.HTTP_201_CREATED,
    summary="Пакетне створення записів",
    responses={
        404: {"description": "Категорію не знайдено"},
        409: {"description": "Дублікат code"},
    },
)
def bulk_create_records(records: schemas.RecordBulk) -> list[dict]:
    """Пакетне створення записів в одній транзакції"""
    try:
        return repository.bulk_create_records(
            records=[record.model_dump() for record in records]
        )
    except ValueError as e:
        raise _error_to_http(e) from e


@router.get(
    "/{record_id}",
    response_model=schemas.RecordRead,
    summary="Отримати запис за його id",
    responses={404: {"description": "Запис не знайдено"}},
)
def get_record(record_id: RecordId) -> dict:
    """Отримати запис за його id"""
    record = repository.get_record(record_id=record_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис з id={record_id} не знайдено",
        )
    return record


@router.get(
    "",
    response_model=list[schemas.RecordRead],
    summary="Отримати список записів",
)
def list_records(
    category_id: int | None = Query(None, gt=0, description="Фільтруємо за категорією"),
    status: schemas.Status | None = Query(None, description="Фільтр за статусом"),  # noqa: B008
    min_value: float | None = Query(
        None,
        ge=config.VALUE_MIN,
        le=config.VALUE_MAX,
        allow_inf_nan=False,
        description="Мінімальне значення",
    ),
    q: str | None = Query(
        None, min_length=1, max_length=120, description="Пошук за назвою"
    ),
    limit: int = Query(20, ge=1, le=100, description="Кількість записів"),
    offset: int = Query(0, ge=0, description="Зсув"),
) -> list[dict]:
    """Отримати список за фільтрами"""
    return repository.list_records(
        category_id=category_id,
        status=status,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.put(
    "/{record_id}",
    response_model=schemas.RecordRead,
    summary="Повністю оновити запис",
    responses={
        404: {"description": "Запис або категорію не знайдено"},
        409: {"description": "Дублікат code"},
    },
)
def replace_record(record_id: RecordId, record: schemas.RecordReplace) -> dict:
    """Повна заміна змінюваних полів запису; id залишається незмінним."""
    try:
        updated = repository.replace_record(
            record_id=record_id,
            code=record.code,
            title=record.title,
            category_id=record.category_id,
            value=record.value,
            status=record.status,
        )
    except ValueError as e:
        raise _error_to_http(e) from e
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис з id={record_id} не знайдено",
        )
    return updated


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити запис",
    responses={404: {"description": "Запис не знайдено"}},
)
def delete_record(record_id: RecordId) -> None:
    """Видалити запис по його id"""
    if not repository.delete_record(record_id=record_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запис з id={record_id} не знайдено",
        )
