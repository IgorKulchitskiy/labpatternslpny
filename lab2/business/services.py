from abc import ABC, abstractmethod


class TestDataService(ABC):

    @abstractmethod
    def import_from_csv(self, path: str):
        pass