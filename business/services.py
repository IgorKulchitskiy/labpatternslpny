from abc import ABC, abstractmethod
from data.entities import TestScenario


class TestDataService(ABC):

    @abstractmethod
    def import_from_csv(self, path: str):
        pass

    @abstractmethod
    def list_scenarios(self) -> list[TestScenario]:
        pass

    @abstractmethod
    def get_scenario(self, scenario_id: int) -> TestScenario | None:
        pass

    @abstractmethod
    def create_scenario(self, name: str, description: str, priority: str) -> TestScenario:
        pass

    @abstractmethod
    def update_scenario(self, scenario_id: int, name: str, description: str, priority: str) -> TestScenario | None:
        pass

    @abstractmethod
    def delete_scenario(self, scenario_id: int) -> bool:
        pass