from functions.parse import parse
from functions.update import update

args = parse()

if __name__ == "__main__":
    update(*args)