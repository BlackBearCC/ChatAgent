import json
from typing import Generator, List, Dict


from simpleaichat.document_loaders.base import BaseDocumentLoader



class JSONLoader(BaseDocumentLoader):
    #可解析的JSON格式

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> List[Dict[str, Dict]]:
        try:
            return self._load_complete_json()
        except json.JSONDecodeError:
            try:
                return self._load_stream_json()
            except Exception as e:
                try:
                    return self._load_jsonl()
                except Exception as e:
                    raise RuntimeError(f"Failed to load JSON file: {e}")

    def _generate_metadata(self, row_number: int) -> Dict:
        """ Generate metadata for a document including file source and row number. """
        return {
            "source": self.file_path,
            "row": row_number
        }

    def _load_complete_json(self) -> List[Dict[str, Dict]]:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return [{"page_content": item, "metadata": self._generate_metadata(row_number)} for row_number, item in
                        enumerate(data, start=1)]
            else:
                return [{"page_content": data, "metadata": self._generate_metadata(1)}]

    def _load_stream_json(self) -> List[Dict[str, Dict]]:
        docs = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for row_number, line in enumerate(file, start=1):
                json_obj = json.loads(line)
                docs.append({"page_content": json_obj, "metadata": self._generate_metadata(row_number)})
        return docs

    def _load_jsonl(self) -> List[Dict[str, Dict]]:
        docs = []
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for row_number, line in enumerate(file, start=1):
                json_obj = json.loads(line)
                docs.append({"page_content": json_obj, "metadata": self._generate_metadata(row_number)})
        return docs



