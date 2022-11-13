import json


def get_keys_and_join_from_currencies_file(key, join_separator):
    f = open('currencies.json', 'r')
    currencies = json.loads(f.read())['currencies']
    f.close()

    return join_separator.join([item[key] for item in currencies])
