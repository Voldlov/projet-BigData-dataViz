cd /opt/workspace &&

pip install -r requirements &&

nohup python twitter_producer.py & &&
nohup python coingecko_producer.py & &&

# Should use spark_submit
nohup python spark_main_WIP.py &