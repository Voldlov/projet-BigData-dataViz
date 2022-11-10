from dotenv import load_dotenv
from kafka import KafkaProducer
import tweepy
import os
import json
import datetime

load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
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

# stream by keywords
keywords = '#XRP OR #DOT OR #CHZ OR #SOL OR #CRO'

stream_tweet.add_rules(tweepy.StreamRule(keywords))
stream_tweet.filter()
