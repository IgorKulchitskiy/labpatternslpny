import csv
import random


scenarios = [
    "Login Test",
    "Registration Test",
    "Add Product to Cart",
    "Checkout Process",
    "Password Reset"
]

descriptions = [
    "User authentication testing",
    "New user registration flow",
    "Adding item to shopping cart",
    "Testing checkout functionality",
    "Password recovery flow"
]

priorities = ["LOW", "MEDIUM", "HIGH"]

actions = [
    "Open page",
    "Enter username",
    "Enter password",
    "Click button",
    "Verify result"
]

expected_results = [
    "Page opens successfully",
    "Login successful",
    "Item added to cart",
    "Checkout completed",
    "Password reset email sent"
]

statuses = ["PASSED", "FAILED", "BLOCKED"]

frameworks = ["Selenium", "Playwright", "Cypress"]

pipelines = ["GitHub CI", "GitLab CI", "Jenkins"]

testers = ["Andriy", "Olena", "Maksym", "Iryna"]

environments = ["Windows", "Linux", "Mac"]

build_versions = ["1.0.0", "1.1.0", "2.0.0"]


def generate_csv(filename="test_data.csv", rows=1200):

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "scenario_id",
            "scenario_name",
            "description",
            "priority",
            "step_number",
            "action",
            "expected_result",
            "result_type",
            "status",
            "tester_name",
            "environment",
            "build_version",
            "framework",
            "execution_time",
            "log_file",
            "ci_pipeline",
            "actual_result"
        ])

        for i in range(rows):

            result_type = random.choice(["MANUAL", "AUTOMATED"])

            writer.writerow([
                random.randint(1, 5),                 # scenario_id
                random.choice(scenarios),             # scenario_name
                random.choice(descriptions),          # description
                random.choice(priorities),            # priority
                random.randint(1, 5),                 # step_number
                random.choice(actions),               # action
                random.choice(expected_results),      # expected_result
                result_type,                          # result_type
                random.choice(statuses),              # status
                random.choice(testers),               # tester_name
                random.choice(environments),          # environment
                random.choice(build_versions),        # build_version
                random.choice(frameworks),            # framework
                random.randint(1, 10),                # execution_time
                "log.txt",                            # log_file
                random.choice(pipelines),             # ci_pipeline
                random.choice(expected_results)       # actual_result
            ])


if __name__ == "__main__":
    generate_csv()
    print("CSV file generated successfully.")