import json
import sqlite3
from contextlib import closing
from pathlib import Path

from labs.lab03.database import get_connection

# для запуску з кореня файлу
BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def load_seed_data() -> dict:
    with open(SEED_PATH, encoding="utf-8") as f:
        return json.load(f)


def seed_database() -> None:
    data = load_seed_data()
    categories = data["categories"]
    records = data["records"]

    with closing(get_connection()) as connection:
        try:
            cursor = connection.execute("SELECT COUNT(*) FROM categories")
            execute_count = cursor.fetchone()[
                0
            ]  # беремо [0], бо sqlite3 завжди повертає кортеж

            if execute_count > 0:
                print(
                    "База даних вже містить категорії. Початкове заповнення пропущено."
                )
                return

            with connection:
                for category in categories:
                    connection.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (category["id"], category["name"]),
                    )

                for record in records:
                    connection.execute(
                        "INSERT INTO records (code, title, category_id, value, status) VALUES (?, ?, ?, ?, ?)",
                        (
                            record["code"],
                            record["title"],
                            record["category_id"],
                            record["value"],
                            record["status"],
                        ),
                    )
            print(
                f"Успішно додано {len(categories)} категорій та {len(records)} записів."
            )

        except sqlite3.IntegrityError as e:
            print(f"Помилка цілісності даних (дані не додано): {e}")
        except json.JSONDecodeError as e:
            print(f"Помилка формату JSON у файлі seed.json: {e}")
        except Exception as e:  # noqa: BLE001
            print(f"Неочікувана помилка під час заповнення бази: {e}")


if __name__ == "__main__":
    seed_database()
