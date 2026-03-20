from abc import ABC, abstractmethod
from data.entities import TestScenario


class TestScenarioRepository(ABC):

    @abstractmethod
    def save(self, scenario: TestScenario):
        pass