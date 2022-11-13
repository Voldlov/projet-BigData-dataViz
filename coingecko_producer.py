from kafka import KafkaProducer
import json
import requests
import time

from tools import get_keys_and_join_from_currencies_file

f = open('currencies.json', 'r')
currencies = json.loads(f.read())['currencies']
f.close()

currencies_id_query_string = get_keys_and_join_from_currencies_file('id', ',')
url = 'https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd'.format(currencies_id_query_string)

producer = KafkaProducer(bootstrap_servers="broker:29092")

while True:
    response = requests.get(url)
    producer.send('cryptos', json.dumps(response.text).encode('utf-8'))
    producer.flush()
    time.sleep(30)
