from api_handlers.google import get_drive_files


def main():
    get_drive_files()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nThank you for using.")
        exit(0)
