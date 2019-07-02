#!/usr/bin/env python3

import os

from api_handlers.google import get_drive_files
from utils.filehandler import get_path
from utils.logger import Logger

LOGGER = Logger(logger_name="Drive2Teams ; Main", filename=None)


def main():
    if not os.path.isfile(get_path("auth", "google.json")):
        LOGGER.fatal("Cannot find google.json in directory auth. Please generate these via the Google Developer Console first.")
        LOGGER.fatal("It can be found here: https://console.developers.google.com/")
        os.mkdir(get_path("auth"), mode=0o755)
        exit(1)

    get_drive_files()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nThank you for using.")
        exit(0)
