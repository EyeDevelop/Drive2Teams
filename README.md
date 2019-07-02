Drive2Teams
---

### NOTE:
**This app cannot be used to upload to Teams yet due
to issues with the Graphs API**

### Why
Because I needed a way for traversing my files automatically from Google Drive to
the Sharepoint folder for one of my Teams. So I created this.

### How to use
#### Requirements
* Python3
* A Google Developer Console ```authentication.json```

First, move the ```authentication.json``` to ```auth/google.json```.
(Create this folder if it doesn't exist)

Then, create a ```drive_documents.json``` file containing the documents you want downloaded
from Google Drive and the format you want them as.

The files will be downloaded in a separate ```drive``` folder with the names as in ```drive_documents.json```.

Run the ```do_the_thing.py``` with Python3.

### The ```drive_documents.json``` format:
```json
{
    "My Filename": {
        "id": "<Google Drive File ID, remove this to search by filename>",
        "type": "<gapps or other, gapps being files made in Google Apps like Docs>",
        "format": "<mimetype to convert file to when using gapps>"
    }
}
```