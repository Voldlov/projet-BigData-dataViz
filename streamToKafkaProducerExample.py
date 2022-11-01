from pykafka import KafkaClient

client = KafkaClient(hosts="127.0.0.1:9092")

topic = client.topics['quickstart']

with topic.get_sync_producer() as producer:
    for i in range(4):
        # The message need to be sent in byte type
        producer.produce('Nouveaux messages'.encode(encoding='UTF-8'))
