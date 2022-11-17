cd /opt/workspace &&

nohup python twitter_producer.py & &&
nohup python coingecko_producer.py & &&

nohup python spark_main.py &