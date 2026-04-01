import json
from abc import ABC, abstractmethod
import urllib.request

class OutputStrategy(ABC):
    @abstractmethod
    def send_data(self, data: dict):
        pass

    def close(self):
        pass

class ConsoleOutputStrategy(OutputStrategy):
    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        category = data.get('Category', 'Unknown')
        print(f"[CONSOLE] ID: {case_id} | Category: {category}")

class RedisOutputStrategy(OutputStrategy):
    def __init__(self, host='localhost', port=6379):
        import redis
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.client.ping()

    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        self.client.set(f"case:{case_id}", json.dumps(data, ensure_ascii=False))
        print(f"[REDIS] Saved: {case_id}")

class KafkaOutputStrategy(OutputStrategy):
    def __init__(self, bootstrap_servers='localhost:9092', topic='lab4'):
        from kafka import KafkaProducer
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )

    def send_data(self, data: dict):
        self.producer.send(self.topic, data)
        print(f"[KAFKA] Sent: {data.get('CaseID')}")

    def close(self):
        self.producer.flush()
        self.producer.close()

class FileOutputStrategy(OutputStrategy):
    def __init__(self, output_filename="output_data.json"):
        self.output_filename = output_filename
        self.data_list = []

    def send_data(self, data: dict):
        self.data_list.append(data)

    def close(self):
        with open(self.output_filename, 'w', encoding='utf-8') as f:
            json.dump(self.data_list, f, ensure_ascii=False, indent=4)

class FireOutputStrategy(OutputStrategy):
    def __init__(self, db_url: str):
        self.db_url = db_url if db_url.endswith('/') else f"{db_url}/"

    def send_data(self, data: dict):
        case_id = data.get('CaseID', 'Unknown')
        url = f"{self.db_url}cases/{case_id}.json"

        payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
        req = urllib.request.Request(url, data=payload, method='PUT')
        req.add_header('Content-Type', 'application/json')

        try:
            urllib.request.urlopen(req)
            print(f"[FIREBASE] Sent: {case_id}")
        except Exception as e:
            print(f"[FIREBASE ERROR] {e}")