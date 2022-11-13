import json


def get_keys_and_join_from_currencies_file(key, join_separator, add_hashtag=False):
    f = open('currencies.json', 'r')
    currencies = json.loads(f.read())['currencies']
    f.close()

    if add_hashtag:
        return join_separator.join(['#{}'.format(item[key]) for item in currencies])
    return join_separator.join([item[key] for item in currencies])
