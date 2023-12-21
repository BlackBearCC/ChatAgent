import csv
import json
from typing import List, Dict, Any, Generator

from simpleaichat.document_loaders.base import BaseDocumentLoader


class TextLoader(BaseDocumentLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[str]:
        return list(self.lazy_load())

    def lazy_load(self) -> Generator[str, None, None]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    yield line.strip()
        except Exception as e:
            print(f"Error reading the text file: {e}")


