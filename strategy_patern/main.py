import json
from copy import deepcopy
from pathlib import Path
from reader import DataReader
from strategies import (
    ConsoleOutputStrategy,
    RedisOutputStrategy,
    KafkaOutputStrategy,
    FileOutputStrategy,
    FireOutputStrategy
)

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"

DEFAULT_CONFIG = {
    "output_strategy": "file",
    "data_source": "api",
    "api_url": "https://data.cityofnewyork.us/resource/erm2-nwe9.json",
    "limit": 20,
    "csv_file_path": "311_cases_100_data.csv",
    "kafka": {
        "bootstrap_servers": "localhost:9092",
        "topic": "lab4"
    },
    "redis": {
        "host": "localhost",
        "port": 6379
    },
    "firebase_url": "https://strategie-63f07-default-rtdb.europe-west1.firebasedatabase.app/"
}

BROKEN_CONFIG = {
    "output_strategy": "unknown_strategy",
    "data_source": "api"
}


def _ask_choice(prompt, valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print(f"Невірний вибір. Доступні варіанти: {', '.join(valid_choices)}")


def _write_config(config_data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config_data, f, ensure_ascii=False, indent=4)
    print(f"Файл конфігурації створено/оновлено: {CONFIG_PATH.name}")


def _ask_output_strategy():
    print("\nОберіть output strategy:")
    print("1 - console")
    print("2 - kafka")
    print("3 - redis")
    print("4 - file")
    choice = _ask_choice("Ваш вибір (1/2/3/4): ", {"1", "2", "3", "4"})

    strategy_by_choice = {
        "1": "console",
        "2": "kafka",
        "3": "redis",
        "4": "file"
    }
    return strategy_by_choice[choice]


def _create_config_menu():
    print("\nОберіть тип конфігу:")
    print("1 - Згенерувати коректний конфіг")
    print("2 - Згенерувати некоректний конфіг (тестовий)")
    choice = _ask_choice("Ваш вибір (1/2): ", {"1", "2"})

    if choice == "1":
        selected_strategy = _ask_output_strategy()
        valid_config = deepcopy(DEFAULT_CONFIG)
        valid_config["output_strategy"] = selected_strategy
        _write_config(valid_config)
    else:
        _write_config(BROKEN_CONFIG)
        print("Згенеровано некоректний конфіг. Наступна перевірка покаже, що він невалідний.")


def validate_config(config):
    errors = []

    if not isinstance(config, dict):
        return False, ["Конфіг має бути JSON-об'єктом."]

    output_strategy = config.get("output_strategy")
    allowed_strategies = {"console", "redis", "kafka", "file", "firebase"}
    if output_strategy not in allowed_strategies:
        errors.append("Поле 'output_strategy' відсутнє або має недопустиме значення.")

    data_source = config.get("data_source")
    if data_source not in {"api", "csv"}:
        errors.append("Поле 'data_source' має бути 'api' або 'csv'.")

    if data_source == "api" and not config.get("api_url"):
        errors.append("Для data_source='api' обов'язкове поле 'api_url'.")

    if data_source == "csv" and not config.get("csv_file_path"):
        errors.append("Для data_source='csv' обов'язкове поле 'csv_file_path'.")

    if output_strategy == "redis":
        redis_conf = config.get("redis")
        if not isinstance(redis_conf, dict) or not redis_conf.get("host"):
            errors.append("Для output_strategy='redis' потрібен блок 'redis' з полем 'host'.")

    if output_strategy == "kafka":
        kafka_conf = config.get("kafka")
        if not isinstance(kafka_conf, dict) or not kafka_conf.get("bootstrap_servers") or not kafka_conf.get("topic"):
            errors.append("Для output_strategy='kafka' потрібен блок 'kafka' з полями 'bootstrap_servers' і 'topic'.")

    if output_strategy == "firebase" and not config.get("firebase_url"):
        errors.append("Для output_strategy='firebase' потрібне поле 'firebase_url'.")

    return len(errors) == 0, errors

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_config():
    while True:
        if not CONFIG_PATH.exists():
            print("\nКонфіг файл не знайдено.")
            print("1 - Створити конфіг")
            print("2 - Вийти")
            print("3 - Згенерувати некоректний конфіг (для перевірки)")
            choice = _ask_choice("Ваш вибір (1/2/3): ", {"1", "2", "3"})

            if choice == "2":
                raise SystemExit("Завершення роботи: без конфіг файлу запуск неможливий.")
            if choice == "3":
                _write_config(BROKEN_CONFIG)
            else:
                _create_config_menu()
            continue

        try:
            config = load_config()
        except json.JSONDecodeError:
            print("\nКонфіг файл знайдено, але JSON некоректний.")
            choice = _ask_choice("Перезаписати файл? (y/n): ", {"y", "n"})
            if choice == "y":
                _create_config_menu()
                continue
            raise SystemExit("Завершення роботи: конфіг файл пошкоджений.")

        is_valid, errors = validate_config(config)
        if not is_valid:
            print("\nКонфіг файл знайдено, але він некоректний:")
            for err in errors:
                print(f"- {err}")

            choice = _ask_choice("Перезаписати конфіг? (y/n): ", {"y", "n"})
            if choice == "y":
                _create_config_menu()
                continue
            raise SystemExit("Завершення роботи: конфіг невалідний.")

        print("\nКонфіг файл знайдено і він коректний.")
        print("1 - Використати існуючий")
        print("2 - Створити новий (перезаписати)")
        print("3 - Вийти")
        choice = _ask_choice("Ваш вибір (1/2/3): ", {"1", "2", "3"})

        if choice == "1":
            return config
        if choice == "2":
            _create_config_menu()
            continue
        raise SystemExit("Завершення роботи за запитом користувача.")

def get_strategy(config):
    strategy_type = config.get("output_strategy")

    if strategy_type == "console":
        return ConsoleOutputStrategy()

    elif strategy_type == "redis":
        redis_conf = config.get("redis", {})
        return RedisOutputStrategy(
            redis_conf.get("host", "localhost"),
            redis_conf.get("port", 6379)
        )

    elif strategy_type == "kafka":
        kafka_conf = config.get("kafka", {})
        return KafkaOutputStrategy(
            kafka_conf.get("bootstrap_servers", "localhost:9092"),
            kafka_conf.get("topic", "lab4")
        )

    elif strategy_type == "file":
        return FileOutputStrategy("output_data.json")

    elif strategy_type == "firebase":
        return FireOutputStrategy(config.get("firebase_url"))

    else:
        raise ValueError("Unknown strategy")

def main():
    config = prepare_config()
    print("\nЗапуск обробки даних...")

    reader = DataReader(config)
    data = reader.read_data()
    print(f"Отримано записів: {len(data)}")

    strategy = get_strategy(config)

    for item in data:
        strategy.send_data(item)

    strategy.close()

    if isinstance(strategy, FileOutputStrategy):
        output_path = Path(__file__).resolve().parent / strategy.output_filename
        print(f"Готово. Дані збережено у файл: {output_path.name}")
    else:
        print("Готово. Дані успішно відправлено через обрану стратегію.")

if __name__ == "__main__":
    main()