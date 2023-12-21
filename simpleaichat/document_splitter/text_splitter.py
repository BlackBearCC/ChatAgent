from typing import Optional, List, Iterable

class Document:
    def __init__(self, page_content: str, metadata: dict):
        self.page_content = page_content
        self.metadata = metadata
class TextSplitter:
    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        keep_separator: bool = True,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.keep_separator = keep_separator
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def _find_separators(self, text):
        positions = []
        for sep in self.separators:
            if sep:
                pos = 0
                while pos != -1:
                    pos = text.find(sep, pos)
                    if pos != -1:
                        positions.append((pos, sep))
                        pos += len(sep)
        positions.sort()
        return positions

    def _split_text(self, text):
        positions = self._find_separators(text)
        start = 0
        chunks = []
        for pos, sep in positions:
            while pos - start >= self.chunk_size:
                end = start + self.chunk_size
                chunks.append(text[start:end])
                start = end - self.chunk_overlap
            if self.keep_separator:
                start = pos + len(sep)
            else:
                start = pos
        if start < len(text):
            chunks.append(text[start:])
        return chunks

    def split_text(self, text):
        return self._split_text(text)

    def split_documents(self, documents: Iterable[dict], text_keys: List[str]) -> List[dict]:
        new_documents = []
        for doc in documents:
            # 检查每个可能的键
            for key in text_keys:
                if key in doc:
                    # 分割找到的文本
                    split_texts = self._split_text(doc[key])
                    for text in split_texts:
                        # 创建一个新文档，保留其他信息
                        new_doc = doc.copy()
                        new_doc[key] = text
                        new_documents.append(new_doc)
                    break  # 找到文本后停止检查其他键
        return new_documents

