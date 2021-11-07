import zipfile
from pathlib import Path
import zipfile
import os


def extract_and_move_healthkit_data():
    downloads_path = str(Path.home() / "Downloads")

    with zipfile.ZipFile(downloads_path + '/export.zip', 'r') as zip_ref:
        zip_ref.extractall('')

if __name__ == '__main__':
    pass
