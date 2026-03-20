from data.repositories import TestScenarioRepository
from data.db import SessionLocal
from data.entities import TestScenario
from sqlalchemy.orm import selectinload


class TestScenarioRepositoryImpl(TestScenarioRepository):

    def save(self, scenario):
        session = SessionLocal()
        try:
            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            return scenario
        finally:
            session.close()

    def get_all(self):
        session = SessionLocal()
        try:
            scenarios = (
                session.query(TestScenario)
                .options(
                    selectinload(TestScenario.steps),
                    selectinload(TestScenario.results)
                )
                .order_by(TestScenario.scenario_id)
                .all()
            )
            return scenarios
        finally:
            session.close()

    def get_by_id(self, scenario_id: int):
        session = SessionLocal()
        try:
            scenario = (
                session.query(TestScenario)
                .options(
                    selectinload(TestScenario.steps),
                    selectinload(TestScenario.results)
                )
                .filter(TestScenario.scenario_id == scenario_id)
                .first()
            )
            return scenario
        finally:
            session.close()

    def update(self, scenario_id: int, name: str, description: str, priority: str):
        session = SessionLocal()
        try:
            scenario = session.query(TestScenario).filter(TestScenario.scenario_id == scenario_id).first()

            if scenario is None:
                return None

            scenario.name = name
            scenario.description = description
            scenario.priority = priority

            session.commit()
            session.refresh(scenario)
            return scenario
        finally:
            session.close()

    def delete(self, scenario_id: int) -> bool:
        session = SessionLocal()
        try:
            scenario = session.query(TestScenario).filter(TestScenario.scenario_id == scenario_id).first()

            if scenario is None:
                return False

            session.delete(scenario)
            session.commit()
            return True
        finally:
            session.close()