# document_loaders/__init__.py

# Import the necessary classes or functions from your modules
from .base import BaseDocumentLoader
from .CSV_loader import CSVLoader
from .JSON_loader import JSONLoader
from .Text_loader import TextLoader

# Optionally, define an __all__ variable that lists the names
# that should be imported when from document_loaders import * is used
__all__ = ['BaseDocumentLoader', 'CSVLoader', 'JSONLoader', 'TextLoader']
