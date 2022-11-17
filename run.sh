cd /opt/workspace &&

pip install -r requirements &&

nohup python twitter_producer.py & &&
nohup python coingecko_producer.py & &&

nohup python spark_main.py &