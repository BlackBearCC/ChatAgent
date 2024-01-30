from langchain_community.document_loaders import CSVLoader, TextLoader
import os

class DataLoader:
    def __init__(self, file_path, autodetect_encoding=True):
        self.file_path = file_path
        self.autodetect_encoding = autodetect_encoding
        self.loader_type = self._detect_file_type()

    def _detect_file_type(self):
        _, file_extension = os.path.splitext(self.file_path)
        if file_extension in ['.csv']:
            return 'csv'
        elif file_extension in ['.json']:
            return 'json'
        elif file_extension in ['.txt']:
            return 'text'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def load(self):
        if self.loader_type == 'csv':
            return CSVLoader(file_path=self.file_path, autodetect_encoding=self.autodetect_encoding).load()
        elif self.loader_type == 'text':
            return TextLoader(file_path=self.file_path, autodetect_encoding=self.autodetect_encoding).load()

        else:
            raise ValueError(f"Unsupported loader type: {self.loader_type}")