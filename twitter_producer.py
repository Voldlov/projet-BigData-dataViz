from dotenv import load_dotenv
from kafka import KafkaProducer
import tweepy
import os
import json
import datetime

from tools import get_keys_and_join_from_currencies_file

load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

currencies_symbol_join_string = get_keys_and_join_from_currencies_file('symbol', ' OR ')

producer = KafkaProducer(bootstrap_servers='broker:29092')


class TweetListener(tweepy.StreamingClient):

    def on_tweet(self, tweet):
        date = datetime.datetime.now()
        data = {
            'text': tweet.text,
            'date': date
        }
        producer.send('tweets', json.dumps(data, indent=4, sort_keys=True, default=str).encode('utf-8'))


stream_tweet = TweetListener(BEARER_TOKEN)
if stream_tweet.get_rules()[0]:
    for rule in stream_tweet.get_rules()[0]:
        stream_tweet.delete_rules(rule.id)

# Rule to filter with either of the given symbol
rule = '({}) -is:retweet -is:reply -is:quote'.format(currencies_symbol_join_string)

stream_tweet.add_rules(tweepy.StreamRule(rule))
stream_tweet.filter()
