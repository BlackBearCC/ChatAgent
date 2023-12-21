import csv
from typing import List, Dict, Any, Generator

from .base import BaseDocumentLoader


class CSVLoader(BaseDocumentLoader):
    def __init__(self,file_path: str):
        self.file_path = file_path

    def load(self) -> List[Dict[str, Any]]:
        documents = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    documents.append(row)
        except Exception as e:
            print(f"Error reading the CSV file: {e}")
        return documents

    def lazy_load(self) -> Generator[Dict[str, Any], None, None]:
        """逐行读取 CSV 文件，并使用生成器逐行返回数据。"""
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    yield row
        except Exception as e:
            print(f"Error reading the CSV file: {e}")


