from data.repositories import TestScenarioRepository
from data.db import SessionLocal


class TestScenarioRepositoryImpl(TestScenarioRepository):

    def save(self, scenario):
        session = SessionLocal()
        session.add(scenario)
        session.commit()
        session.close()