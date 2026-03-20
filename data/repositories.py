from abc import ABC, abstractmethod
from data.entities import TestScenario


class TestScenarioRepository(ABC):

    @abstractmethod
    def save(self, scenario: TestScenario):
        pass

    @abstractmethod
    def get_all(self) -> list[TestScenario]:
        pass

    @abstractmethod
    def get_by_id(self, scenario_id: int) -> TestScenario | None:
        pass

    @abstractmethod
    def update(self, scenario_id: int, name: str, description: str, priority: str) -> TestScenario | None:
        pass

    @abstractmethod
    def delete(self, scenario_id: int) -> bool:
        pass