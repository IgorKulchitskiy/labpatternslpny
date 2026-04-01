import json
from reader import DataReader
from strategies import (
    ConsoleOutputStrategy,
    RedisOutputStrategy,
    KafkaOutputStrategy,
    FileOutputStrategy,
    FireOutputStrategy
)

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

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
    config = load_config()

    reader = DataReader(config)
    data = reader.read_data()

    strategy = get_strategy(config)

    for item in data:
        strategy.send_data(item)

    strategy.close()

if __name__ == "__main__":
    main()