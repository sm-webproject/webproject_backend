import os
import sys


def main():
    os.chdir('app')
    os.system("uvicorn main:app --reload")


def commit():
    os.chdir('app')

    if len(sys.argv) != 2:
        print('poetry run commit <message>')
        return

    msg = sys.argv[1]
    os.system(f"alembic revision --autogenerate -m \"{msg}\"")


def push():
    os.chdir('app')

    os.system("alembic upgrade head")


def lint():
    os.system("pylint app")
