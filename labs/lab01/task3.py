import csv
import datetime
import hashlib
import json
import os
import random
import sys

from tabulate import tabulate

sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")))

from shared.student import VARIANT_NUMBER

# md5
MIN_PASS_LENGHT = 8
SALT = f"{VARIANT_NUMBER:05d}"

users_to_register = (
    ("m_verstappen", "RedBull#1"),
    ("l_hamilton", "SirLewis44!"),
    ("c_leclerc", "Monaco16!"),
    ("f_alonso", "ElPlan14!"),
    ("m_schumacher", "KeepFighting7"),
    ("r_marciello", "BMW_M4_GT3"),
    ("j_gounon", "AMG_GT3_2026"),
    ("l_vanthoor", "Porsche911GT3"),
    ("k_vanderlinde", "AudiR8_GT3"),
    ("d_vanthoor", "BMW_Factory1"),
)


class ValidationError(Exception):
    pass


def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError
    if len(password) < MIN_PASS_LENGHT:
        raise ValidationError

    nohash = (password + salt).encode("utf-8")
    return hashlib.md5(nohash).hexdigest()


def create_user(username, password):
    return (username, generate_hash(password, SALT))


def create_users(users_list):
    os.makedirs("labs/lab01/data", exist_ok=True)

    uxxx = [create_user(username, password)
            for username, password in users_list]

    with open("labs/lab01/data/users.csv", mode="w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(uxxx)


def red_user():
    user_bd = []
    with open("labs/lab01/data/users.csv", mode="r", encoding="utf-8") as f:
        for i in csv.reader(f):
            if i:
                user_bd.append(i)
        return user_bd


def log_event(func):
    def wkladena(username, password, *args, **kwargs):
        reusltquick = func(username, password, *args, **kwargs)
        result = "success" if reusltquick else "failure"

        logs = []
        if os.path.exists("labs/lab01/data/log.json") and os.path.getsize(
                "labs/lab01/data/log.json") > 0:
            with open("labs/lab01/data/log.json", "r", encoding="utf-8") as f:
                logs = json.load(f)
        log_enter = {
            "event": "login",
            "user": username,
            "result": result,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # noqa: DTZ005
            "args": list(args),
            "kwargs": kwargs
        }
        logs.append(log_enter)

        with open("labs/lab01/data/log.json", "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)

        return reusltquick
    return wkladena


@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError
    hashpass = generate_hash(password, SALT)
    for username_bd, hash_bd in user_bd:
        if username_bd == username and hash_bd == hashpass:
            return True
    return False


if __name__ == "__main__":
    try:
        create_users(users_to_register)
        user_bd = red_user()

        rand_user, rand_pass = random.choice(users_to_register)
        login(rand_user, rand_pass)

        print(tabulate(user_bd, headers=["Логін", "MD5"], tablefmt="grid"))
    except (OSError, FileNotFoundError, PermissionError, ValidationError, ValueError) as error:
        print(error)
