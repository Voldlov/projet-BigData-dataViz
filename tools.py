import json


def get_currencies():
    f = open('currencies.json', 'r')
    currencies = json.loads(f.read())['currencies']
    f.close()
    return currencies


def get_list_of_keys(key):
    currencies = get_currencies()

    return [item[key] for item in currencies]


def get_keys_and_join_from_currencies_file(key, join_separator, add_hashtag=False):
    currencies = get_currencies()

    if add_hashtag:
        return join_separator.join(['#{}'.format(item[key]) for item in currencies])
    return join_separator.join([item[key] for item in currencies])
