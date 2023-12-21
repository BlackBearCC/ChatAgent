import json
from typing import Generator

import ijson

from simpleaichat.document_loaders.base import BaseDocumentLoader



class JSONLoader(BaseDocumentLoader):
    #可解析的JSON格式

    def __init__(self,file_path: str):
        self.file_path = file_path

    def load(self):
        try:
            # 尝试作为一个完整的 JSON 对象加载
            return self._load_complete_json()
        except json.JSONDecodeError:
            try:
                # 尝试作为 JSON 数组进行流式加载
                return self._load_stream_json()
            except Exception as e:
                try:
                    # 尝试作为 JSON Lines 文件进行加载
                    return self._load_jsonl()
                except Exception as e:
                    raise RuntimeError(f"Failed to load JSON file: {e}")

    def _load_jsonl(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return [json.loads(line) for line in file if line.strip()]
    def _load_complete_json(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _load_stream_json(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            parser = ijson.items(file, 'item')
            return [item for item in parser]

    def lazy_load(self) -> Generator[dict, None, None]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip():  # 确保不处理空行
                        yield json.loads(line)
        except Exception as e:
            print(f"Error reading the JSON file: {e}")



