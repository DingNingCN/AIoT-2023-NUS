import random
import time
import mysql.connector

import joblib

import paho.mqtt.client as mqtt

from datetime import datetime
from sklearn.preprocessing import MinMaxScaler


def on_connect(client, userdata, flags, rc):
	
	if rc == 0:
	
		print("Connected to MQTT Broker!")
		
	else:
	
		print('Failed to connect, return code {:d}'.format(rc))



def on_message(client, userdata, msg):
	
	print('Received:{}'.format(msg.payload.decode()))
	
	# 获取当前时间
	now = datetime.now()

	# 提取小时、分钟和秒，并以两位数显示
	hour = str(now.hour).zfill(2)
	minute = str(now.minute).zfill(2)
	second = str(now.second).zfill(2)

	# 打印小时、分钟和秒
	print("当前时间：{}:{}:{}".format(hour, minute, second))


	# 使用逗号进行分割
	temp, humidity, pressure, light, rainfall, vehicles = msg.payload.decode().split(",")

	# 打印分割后的值
	print("温度：", temp)
	print("湿度：", humidity)
	print("压力：", pressure)
	print("光照：", light)

	# 建立MySQL数据库连接
	cnx = mysql.connector.connect(
		host="localhost",
		user="root",
		password="123456",
		database="aiot"
	)

	# 检查是否与数据库建立连接
	# if cnx.is_connected():
	# 	print("已成功连接到MySQL数据库")
	# else:
	# 	print("无法连接到MySQL数据库")



	# 创建一个数据库游标
	cursor = cnx.cursor()

	rfc = joblib.load("rfc.pkl")
	new_data = [[7, 14, hour, temp, 1, humidity, pressure]]
	scaler = MinMaxScaler()
	X_scaled = scaler.fit_transform(new_data)

	def map_weather(x):
		if x == 0:
			return 'sunny'
		elif x == 1:
			return 'cloudy'
		elif x == 2:
			return 'overcast'
		elif x == 3:
			return 'foggy'
		elif x == 4:
			return 'rainy'

	y_pred = rfc.predict(X_scaled)
	weather = map_weather(y_pred)

	print(weather)

	# 准备SQL查询语句
	query = "INSERT INTO aiot (Temperaturevalue, Humidityvalue, atmos, Brightnessvalue, Weathername,  Hour, Minute, Second) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

	# 执行SQL查询语句，将数据插入到数据库中
	data = (temp, humidity, pressure, light, weather, hour, minute, second)
	cursor.execute(query, data)

	# 提交更改到数据库
	cnx.commit()

	# 关闭数据库连接
	cursor.close()
	cnx.close()




def run():

	try:
	
		broker = 'broker.emqx.io'
		port = 1883
		topic = "/is4151-is5451/lab06"
		client_id = f'python-mqtt-{random.randint(0, 10000)}'
		username = 'emqx'
		password = 'public'

		print('client_id={}'.format(client_id))



		# Set Connecting Client ID
		client = mqtt.Client(client_id)
		client.username_pw_set(username, password)
		client.on_connect = on_connect
		client.connect(broker, port)
		
		client.subscribe(topic)
		client.on_message = on_message

		client.loop_forever()				

	except KeyboardInterrupt:

			print('Program terminated!')



if __name__ == '__main__':
	
	run()