import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             '../../')))
from labs.lab01 import task1, task2, task3


def main():
    while True:
        number = int(
            input(
                "Введіть номер задавння (введіть 0 щоб завершити перегляд): "))
        if number == 1:
            print("Завдання 1")
            task1.main()
        elif number == 2:
            print("Завдання 2")
            task2.main()
        elif number == 3:
            print("Завдання 3")
            task3.main()
        elif number == 0:
            print("Дякую за перегляд")
            break

        else:
            print("Не вірний номер")


if __name__ == "__main__":
    main()
