from kafka import KafkaProducer
import json
import requests
import time
from datetime import datetime, timedelta

from tools import get_keys_and_join_from_currencies_file, get_symbol_from_name

currencies_id_query_string = get_keys_and_join_from_currencies_file('id', ',')
url = 'https://api.coingecko.com/api/v3/simple/price?ids={}&vs_currencies=usd'.format(currencies_id_query_string)

producer = KafkaProducer(bootstrap_servers="broker:29092")

while True:
    response = requests.get(url)

    for crypto in response.json():
        data = {
            "name": crypto,
            "symbol": get_symbol_from_name(crypto),
            "value": response.json()[crypto]['usd'],
            "date": (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }
        producer.send('crypto', json.dumps(data).encode('utf-8'))
    time.sleep(30)
