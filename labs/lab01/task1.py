import os
import random
import sys

from tabulate import tabulate

from shared.student import STUDENT_NAME

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../')))

passwords = ["SIEM@An4lysis", "easy123", "S0C@Analyst", "observer",
             "Threat@Hunt1ng", "viewer", "Incid3nt@Handle", "monitor",
             "Log@An4lysis", "watcher"]
criteria = {"min_length": 9, "require_digits": True, "require_upper": True,
            "require_special": True}
forbidden_passwords = {"easy123", "observer", "viewer", "monitor", "watcher",
                       "admin"}


def prohibited_password(passw, forbidden_passwords):
    return passw in forbidden_passwords or len(passw) < criteria["min_length"]


def weak_password(passw, forbidden_passwords):
    has_digit, has_upper, has_lower, has_special = get_char_flags(passw)
    return passw not in forbidden_passwords and (
        has_digit or has_lower or has_special or has_upper)


def average_password(passw):
    has_digit, has_upper, has_lower, has_special = get_char_flags(passw)
    return len(passw) >= criteria["min_length"] and (
        has_digit or has_lower or has_special or has_upper)


def strong_password(passw):
    has_digit, has_upper, has_lower, has_special = get_char_flags(passw)
    return len(passw) >= (criteria["min_length"]) and (
        has_digit and has_lower and has_special and has_upper)


def very_strong_password(passw, passwords):
    has_digit, has_upper, has_lower, has_special = get_char_flags(passw)
    return len(passw) >= (criteria["min_length"] + 4) and (has_digit and has_lower and has_special and has_upper) and passwords.count(passw) == 1


def get_char_flags(passw):
    has_digit = any(char.isdigit() for char in passw)
    has_upper = any(char.isupper() for char in passw)
    has_lower = any(char.islower() for char in passw)
    has_special = any(not char.isalnum() for char in passw)
    return has_digit, has_upper, has_lower, has_special


def get_status(passw, passwords, forbidden_passwords):
    if prohibited_password(passw, forbidden_passwords):
        return "Заборонений"
    if very_strong_password(passw, passwords):
        return "Дуже сильний"
    if strong_password(passw):
        return "Сильний"
    if average_password(passw):
        return "Середній"
    if weak_password(passw, forbidden_passwords):
        return "Слабкий"
    return "Заборонений"


for idx in random.sample(range(len(passwords)), 3):
    passwords.append(passwords[idx])

table_data = []
for passw in passwords:
    table_data.append(
        [passw, get_status(passw, passwords, forbidden_passwords)])

headers = ["Пароль", "Результат"]
print(STUDENT_NAME)
print(tabulate(table_data, headers=headers, tablefmt="grid"))
