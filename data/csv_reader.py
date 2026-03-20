import csv


class CsvTestDataReader:

    def read(self, path: str):
        with open(path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)