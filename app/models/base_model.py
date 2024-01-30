from abc import ABC, abstractmethod

from pydantic import BaseModel


class Base(BaseModel):

    @abstractmethod
    def update(self):
        pass
