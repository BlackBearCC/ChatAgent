from typing import List, Generator, Any
from abc import ABC, abstractmethod

# Define an abstract base class for a document loader
class BaseDocumentLoader(ABC):
    @abstractmethod
    def load(self) -> List[Any]:
        """
        Load data and return as a list of items.
        Implement this method in subclasses to define how data is loaded.
        """
        pass


    def lazy_load(self) -> Generator[Any, None, None]:
        """
        A generator for lazy loading of documents.
        Yields items one by one.
        """
        for item in self.load():
            yield item

# Define an abstract base class for a blob parser
class BaseBlobParser(ABC):
    @abstractmethod
    def parse(self, blob: Any) -> List[Any]:
        """
        Parse a blob into a list of items.
        Implement this method in subclasses to define how blobs are parsed.
        """
        pass

    @abstractmethod
    def lazy_parse(self, blob: Any) -> Generator[Any, None, None]:
        """
        A generator for lazy parsing of blobs.
        Yields parsed items one by one.
        """
        for item in self.parse(blob):
            yield item



# # Usage
# loader = MyDocumentLoader()
# for doc in loader.lazy_load():
#     print(f"Loaded: {doc}")
#
# parser = MyBlobParser()
# blob = "This is a sample blob"
# for parsed_item in parser.lazy_parse(blob):
#     print(f"Parsed: {parsed_item}")
