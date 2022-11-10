from kafka import KafkaProducer
import json
import requests
import time

url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
producer = KafkaProducer(bootstrap_servers="broker:29092")

while True:
    response = requests.get(url)
    producer.send('cryptos', json.dumps(response.text).encode('utf-8'))
    producer.flush()
    time.sleep(10)