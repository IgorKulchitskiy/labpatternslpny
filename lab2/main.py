from data.db import init_db
from data.repositories_impl import TestScenarioRepositoryImpl
from data.csv_reader import CsvTestDataReader
from business.services_impl import TestDataServiceImpl
from generator.csv_generator import generate_csv

def main():

    generate_csv("test_data.csv", rows=1200)

    init_db()

    repository = TestScenarioRepositoryImpl()
    reader = CsvTestDataReader()

    service = TestDataServiceImpl(repository, reader)

    service.import_from_csv("test_data.csv")

    print("Data successfully imported into database.")


if __name__ == "__main__":
    main()