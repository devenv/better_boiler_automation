import sys
from modules import modules_by_name


if __name__ == "__main__":
    name = sys.argv[1]
    modules_by_name[name]().run()