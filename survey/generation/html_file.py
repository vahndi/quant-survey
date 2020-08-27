from pathlib import Path


class HtmlFile(object):
    """
    Context manager to open and write to a new .html file.
    """
    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def __enter__(self):
        self.open_file = open(self.file_path, 'w')
        self.open_file.write('<!DOCTYPE html>\n')
        return self.open_file

    def __exit__(self, *args):
        self.open_file.close()
