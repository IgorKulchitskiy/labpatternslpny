from abc import ABC, abstractmethod


class TestDataController(ABC):

    @abstractmethod
    def upload_csv(self, path: str):
        pass