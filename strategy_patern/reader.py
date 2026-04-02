import requests
import csv

class DataReader:
    def __init__(self, config):
        self.config = config

    def read_data(self):
        if self.config.get("data_source") == "api":
            return self._read_from_api()
        else:
            return self._read_from_csv()

    def _read_from_api(self):
        url = self.config.get(
            "api_url",
            "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
        )
        limit = self.config.get("limit", 100)

        response = requests.get(url, params={"$limit": limit})
        data = response.json()

        result = []

        for item in data:
            mapped = {
                "CaseID": item.get("unique_key", "Unknown"),
                "Category": item.get("complaint_type", "Unknown"),
                "Agency": item.get("agency", ""),
                "Borough": item.get("borough", ""),
                "CreatedDate": item.get("created_date", "")
            }
            result.append(mapped)

        return result

    def _read_from_csv(self):
        path = self.config.get("csv_file_path")

        result = []
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                result.append(row)

        return result