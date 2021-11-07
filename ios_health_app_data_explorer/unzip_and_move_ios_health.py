from pathlib import Path
import zipfile
import os


def extract_and_move_healthkit_data():
    """Assumes healthkit zip file is located in the Downloads folder.  Unzips it and
    exports the contents to the current working directory.
    """

    downloads_path = str(Path.home() / "Downloads")

    with zipfile.ZipFile(downloads_path + "/export.zip", "r") as zip_ref:
        zip_ref.extractall(os.getcwd())  # To current working directory.


if __name__ == "__main__":
    extract_and_move_healthkit_data()
