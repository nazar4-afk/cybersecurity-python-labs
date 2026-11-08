"""Шар доступу до даних для лабораторної роботи №3 (варіант 11)."""

import sqlite3
from contextlib import closing

from labs.lab03.database import get_connection


def _record_from_row(row):
    """Перетворити рядок результату JOIN на словник."""
    return {
        "id": row[0],
        "code": row[1],
        "title": row[2],
        "category_id": row[3],
        "value": row[4],
        "status": row[5],
        "category_name": row[6],
    }


def create_category(name):
    """Створення категорії. Повертає {'id': ..., 'name': ...}."""
    with closing(get_connection()) as connection:
        try:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO categories (name) VALUES (?)", (name,)
                )
                return {"id": cursor.lastrowid, "name": name}
        except sqlite3.IntegrityError:
            raise ValueError(f"Категорія з назвою '{name}' вже існує")


def list_categories():
    """Отримання списку категорій."""
    with closing(get_connection()) as connection:
        cursor = connection.execute("SELECT id, name FROM categories ORDER BY id")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]


def delete_category(category_id):
    """Видалення порожньої категорії."""
    with closing(get_connection()) as connection:
        try:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM categories WHERE id = ?", (category_id,)
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Категорія з id={category_id} не знайдена")
        except sqlite3.IntegrityError:
            raise ValueError(
                f"Категорія з id={category_id} має записи і не може бути видалена"
            )


def create_record(code, title, category_id, value, status):
    """Створити запис. Повертає словник з даними запису."""
    with closing(get_connection()) as connection:
        category = connection.execute(
            "SELECT id FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if category is None:
            raise ValueError(f"Категорія з id={category_id} не знайдена")

        try:
            with connection:
                cursor = connection.execute(
                    "INSERT INTO records (code, title, category_id, value, status) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (code, title, category_id, value, status),
                )
                record_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Дублікат code: '{code}'")

        row = connection.execute(
            "SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name "
            "FROM records r JOIN categories c ON r.category_id = c.id "
            "WHERE r.id = ?",
            (record_id,),
        ).fetchone()

        return _record_from_row(row)


def get_record(record_id):
    """Отримання запису за id."""
    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name "
            "FROM records r JOIN categories c ON r.category_id = c.id "
            "WHERE r.id = ?",
            (record_id,),
        )
        row = cursor.fetchone()
        if row is not None:
            return _record_from_row(row)


def list_records(
    category_id=None, status=None, min_value=None, q=None, limit=20, offset=0
):
    """Отримання списку записів із фільтрами та поділом на сторінки."""
    conditions = []
    params = []

    if category_id is not None:
        conditions.append("r.category_id = ?")
        params.append(category_id)
    if status is not None:
        conditions.append("r.status = ?")
        params.append(status)
    if min_value is not None:
        conditions.append("r.value >= ?")
        params.append(min_value)
    if q is not None:
        conditions.append("instr(r.title, ?) > 0")
        params.append(q)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql_command = (
        "SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name "
        "FROM records r JOIN categories c ON r.category_id = c.id "
        f"WHERE {where_clause} ORDER BY r.id LIMIT ? OFFSET ?"
    )

    params.extend([limit, offset])

    with closing(get_connection()) as connection:
        cursor = connection.execute(sql_command, params)
        return [_record_from_row(row) for row in cursor.fetchall()]


def replace_record(record_id, code, title, category_id, value, status):
    """Повне оновлення змінюваних полів запису; id залишається незмінним."""
    with closing(get_connection()) as connection:
        existing = connection.execute(
            "SELECT id FROM records WHERE id = ?", (record_id,)
        ).fetchone()
        if existing is not None:
            category = connection.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
            if category is None:
                raise ValueError(f"Категорія з id={category_id} не знайдена")

            try:
                with connection:
                    connection.execute(
                        "UPDATE records SET code=?, title=?, category_id=?, value=?, status=? "
                        "WHERE id=?",
                        (code, title, category_id, value, status, record_id),
                    )
            except sqlite3.IntegrityError:
                raise ValueError(f"Дублікат в code: '{code}'")

            row = connection.execute(
                "SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name "
                "FROM records r JOIN categories c ON r.category_id = c.id "
                "WHERE r.id = ?",
                (record_id,),
            ).fetchone()
            return _record_from_row(row)


def delete_record(record_id):
    """Видалити запис. Повертає True якщо видалено, False якщо не знайдено."""
    with closing(get_connection()) as connection:
        existing = connection.execute(
            "SELECT id FROM records WHERE id = ?", (record_id,)
        ).fetchone()

        if existing is None:
            return False

        with connection:
            connection.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return True


def bulk_create_records(records):
    """Пакетне додавання записів у межах однієї транзакції."""
    with closing(get_connection()) as connection:
        category_ids = {r["category_id"] for r in records}
        for cat_id in category_ids:
            category = connection.execute(
                "SELECT id FROM categories WHERE id = ?", (cat_id,)
            ).fetchone()
            if category is None:
                raise ValueError(f"Категорія з id={cat_id} не знайдена")

        created_ids = []
        try:
            with connection:
                for record in records:
                    cursor = connection.execute(
                        "INSERT INTO records (code, title, category_id, value, status) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (
                            record["code"],
                            record["title"],
                            record["category_id"],
                            record["value"],
                            record["status"],
                        ),
                    )
                    created_ids.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            raise ValueError(
                "Дублікат code у пакеті або в базі. Жоден запис не збережено."
            )

        placeholders = ",".join("?" * len(created_ids))
        cursor = connection.execute(
            f"SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name "
            f"FROM records r JOIN categories c ON r.category_id = c.id "
            f"WHERE r.id IN ({placeholders}) ORDER BY r.id",
            created_ids,
        )
        return [_record_from_row(row) for row in cursor.fetchall()]
