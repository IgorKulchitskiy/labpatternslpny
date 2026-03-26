from datetime import date
from business.services import TestDataService
from data.entities import (
    TestScenario,
    TestStep,
    ManualTestResult,
    AutomatedTestResult,
    TestStatus
)


class TestDataServiceImpl(TestDataService):

    def __init__(self, repository, csv_reader):
        self.repository = repository
        self.csv_reader = csv_reader

    def import_from_csv(self, path: str):

        rows = self.csv_reader.read(path)

        scenarios = {}

        for row in rows:

            scenario_id = int(row["scenario_id"])

            if scenario_id not in scenarios:
                scenarios[scenario_id] = TestScenario(
                    scenario_id=scenario_id,
                    name=row["scenario_name"],
                    description=row["description"],
                    priority=row["priority"]
                )

            scenario = scenarios[scenario_id]

            step = TestStep(
                step_number=int(row["step_number"]),
                action=row["action"],
                expected_result=row["expected_result"]
            )

            scenario.steps.append(step)

            if row["result_type"] == "MANUAL":

                result = ManualTestResult(
                    execution_date=date.today(),
                    status=TestStatus[row["status"]],
                    tester_name=row["tester_name"],
                    environment=row["environment"],
                    build_version=row["build_version"],
                    actual_result=row["actual_result"]
                )

            else:

                result = AutomatedTestResult(
                    execution_date=date.today(),
                    status=TestStatus[row["status"]],
                    framework=row["framework"],
                    execution_time=int(row["execution_time"]),
                    log_file=row["log_file"],
                    ci_pipeline=row["ci_pipeline"],
                    actual_result=row["actual_result"]
                )

            scenario.results.append(result)

        for scenario in scenarios.values():
            self.repository.save(scenario)

    def list_scenarios(self):
        return self.repository.get_all()

    def get_scenario(self, scenario_id: int):
        return self.repository.get_by_id(scenario_id)

    def create_scenario(self, name: str, description: str, priority: str):
        scenario = TestScenario(
            name=name,
            description=description,
            priority=priority
        )
        return self.repository.save(scenario)

    def update_scenario(self, scenario_id: int, name: str, description: str, priority: str):
        return self.repository.update(scenario_id, name, description, priority)

    def delete_scenario(self, scenario_id: int):
        return self.repository.delete(scenario_id)