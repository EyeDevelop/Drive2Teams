import os

# Set the base directory to this project folder.
BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_path(*path):
    """
    Helper function to get files relative to project directory.

    :param path: A list of directories with a file at the end. Same usage as in os.path.
    :return: The file path, if it exists.
    """

    return os.path.join(BASE_DIRECTORY, *path)
