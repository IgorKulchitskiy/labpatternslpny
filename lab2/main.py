import os
from data.db import init_db
from data.repositories_impl import TestScenarioRepositoryImpl
from data.csv_reader import CsvTestDataReader
from business.services_impl import TestDataServiceImpl
from presentation.controllers import TestScenarioWebController


def build_service():
    repository = TestScenarioRepositoryImpl()
    reader = CsvTestDataReader()
    return TestDataServiceImpl(repository, reader)


def seed_if_needed(service):
    if service.list_scenarios():
        return

    if os.path.exists("test_data.csv"):
        service.import_from_csv("test_data.csv")

def main():
    init_db()
    service = build_service()
    seed_if_needed(service)

    controller = TestScenarioWebController(service)
    app = controller.create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()