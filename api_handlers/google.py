import json
import mimetypes
import os
import pickle

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from utils.logger import Logger
from utils.filehandler import get_path

LOGGER = Logger(logger_name="Drive2Teams ; Drive", filename=None)
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]  # Remove file token.pickle if changing these.


def sign_in():
    """
    Log in to the Google Drive API.
    This is done by first loading a token.pickle file if it exists (also refreshes the token if necessary),
    or by logging in using a google.json when it doesn't.

    The token.pickle file is created automatically when the authorisation process
    completes successfully.

    :return: A credentials object.
    """

    LOGGER.debug("Trying to sign in.")

    # First try to load the token.pickle.
    creds = None
    if os.path.isfile(get_path("auth", "token.pickle")):
        LOGGER.debug("File token.pickle found.")

        with open(get_path("auth", "token.pickle"), "rb") as token_fp:
            try:
                creds = pickle.load(token_fp)
                LOGGER.debug("Credentials valid: %s" % creds.valid)

            except NameError as exc:
                LOGGER.err("Failed to load token.pickle: File invalid.")
                creds = None

            except Exception as exc:
                LOGGER.err("Failed to load token.pickle: %s" % exc)
                creds = None

        # Check if it needs a refresher.
        if not creds.valid and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = None

    # Do the login using google.json
    if not creds:
        LOGGER.debug("Falling back to google.json log in.")

        flow = InstalledAppFlow.from_client_secrets_file(get_path("auth", "google.json"), SCOPES)
        creds = flow.run_local_server(port=0)

    # Save the credentials for next time.
    with open(get_path("auth", "token.pickle"), "wb") as token_fp:
        pickle.dump(creds, token_fp)

        LOGGER.debug("Saved token.pickle for next use.")

    LOGGER.info("Logged in successfully.")

    return creds


def get_id_for_drive_filename(drive_filename, service):
    """
    Try to translate a filename to a Google Drive ID. If multiple files are found, it will use only the first.

    :param drive_filename: The file as named on Google Drive.
    :param service: The Drive service object.

    :return: The ID associated with the file, or None when not found.
    """

    page_token = None

    while True:
        response = service.files().list(
            q="name = '%s'" % drive_filename,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token
        ).execute()

        response_len = len(response.get("files", []))
        if response_len >= 1:
            if response_len > 1:
                LOGGER.warn("Found more than one file for %s. Using only first one." % drive_filename)

            return response.get("files", [])[0].get("id")

        page_token = response.get("nextPageToken", None)
        if not page_token:
            LOGGER.err("File not found on Google Drive.")
            break

    return None


def download_google_drive_file(filename, drive_file_id, service):
    """
    Download the Google Drive file using the ID.

    :param filename: The filename to save it as.
    :param drive_file_id: The ID of the file to download.
    :param service: The Drive service object.

    :return: Nothing.
    """

    request = service.files().get_media(fileId=drive_file_id)

    # First check if the drive directory exists. Create it if it doesn't.
    if not os.path.isdir(get_path("drive")):
        os.mkdir(get_path("drive"), mode=0o755)

    # Do the actual download.
    LOGGER.info("Downloading file %s..." % filename)
    with open(get_path("drive", filename), "wb") as fp:
        downloader = MediaIoBaseDownload(fp, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()


def download_google_docs_file(filename, drive_file_id, service, file_mimetype):
    """
    Download a Google Docs document using the ID.

    :param filename: The filename to save it as.
    :param drive_file_id: The ID of the document to download.
    :param service: The Drive service object.
    :param file_mimetype: The mimetype to download the document as, defaults to docx.

    :return: Boolean of success.
    """

    request = service.files().export_media(fileId=drive_file_id, mimeType=file_mimetype)

    # First check if the drive directory exists. Create it if it doesn't.
    if not os.path.isdir(get_path("drive")):
        os.mkdir(get_path("drive"), mode=0o755)

    # Do the download.
    LOGGER.info("Downloading document %s..." % (filename + mimetypes.guess_extension(file_mimetype)))
    with open(get_path("drive", filename + mimetypes.guess_extension(file_mimetype)), "wb") as fp:
        downloader = MediaIoBaseDownload(fp, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()


def get_drive_files():
    """
    Read file documents.json to get the files wanted. Then, download these files as docx.

    :return: Nothing.
    """

    # Get access to Google Drive first.
    service = build("drive", "v3", credentials=sign_in())

    # Check if the documents.json exists, if not, create it.
    if not os.path.isfile(get_path("documents.json")):
        LOGGER.debug("documents.json not found. Making a dummy.")

        with open(get_path("documents.json"), "wt") as requested_fp:
            json.dump({}, requested_fp)

    # Get the files we need from documents.json.
    with open("documents.json", "rt") as requested_fp:
        LOGGER.debug("Loading documents.json")
        requested = json.load(requested_fp)

    # Search for the files in Google Drive,
    # and download them to a separate directory
    # converted to docx.
    for filename, file in requested.items():
        LOGGER.debug("Started to fetch all documents.")

        # Try to get the file ID so it can be downloaded.
        if "id" not in file.keys():
            LOGGER.debug("ID not found in documents.json for %s. Trying to fetch based on filename." % filename)
            drive_file_id = get_id_for_drive_filename(filename, service)
        else:
            drive_file_id = file["id"]

        if not drive_file_id:
            LOGGER.err("Skipping file %s as no ID is retrieved." % filename)
            continue

        # If it is a Google Apps generated file, get the mimetype to download file as.
        # If none is specified, pdf is chosen as default.
        if "format" in file.keys():
            mimetype = file["format"]
        else:
            # mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  # Google Document --> MS Word Docx
            mimetype = "application/pdf"

        # Get if this file is a Google Apps generated one.
        if "type" not in file.keys():
            file["type"] = "other"

        file_type = file["type"]
        if file_type not in ["gapps", "other"]:
            LOGGER.err("Skipping file for wrong type. Only 'gapps' and 'other' allowed.")
            continue

        # Try to download the file.
        LOGGER.debug("Started download for %s:%s with type %s" % (filename, drive_file_id, file_type))

        if file_type == "gapps":
            download_google_docs_file(filename, drive_file_id, service, mimetype)
        else:
            download_google_drive_file(filename, drive_file_id, service)
