#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import sys
import os
import traceback
import json
import subprocess
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import MyServer.common as MyCom


'''
センサーで測距した距離データをMQTTで送信する
https://pypi.org/project/paho-mqtt/
https://qiita.com/hsgucci/items/6461d8555ea1245ef6c2
http://www.steves-internet-guide.com/loop-python-mqtt-client/


'''

debug_mode = True
#debug_mode = False

# config.jsonを読み、パラメータを取得
MyCom.load_config('./config_slack.json')
my_id = MyCom.id()
interval = MyCom.interval()
app_id = MyCom.app_id()
mqtt_broker = MyCom.mqtt()
topic_pub = MyCom.topic_monitor()
topic_sub = MyCom.topic_event()
mqtt_broker_addr = mqtt_broker.split(':')[0]
mqtt_broker_port = int(mqtt_broker.split(':')[1])

# トピック
topic_pub = os.path.join(app_id, topic_pub)
topic_sub = os.path.join(app_id, topic_sub)

if debug_mode:
    print(mqtt_broker_addr)
    print(mqtt_broker_port)
    print(topic_pub)
    print(topic_sub)


# アクション実行
def do_action(cmd, opt):
    if debug_mode:
        print("do_action:" + cmd + " " + opt)
    ret = subprocess.call([cmd, opt])
    return ret


# MQTT接続時にサブスクライバを登録する関数
def regist_sub(cl, info, flag, rc):
    if debug_mode:
        print("regist_sub:", rc)

    if rc != 0:
        print("Failed to connect MQTT Broker.", + str(rc))
        os.exit(1)

    if debug_mode:
        print("subscribe:" + topic_sub)

    cl.subscribe(topic_sub)


# メッセージ到着時のアクション実行コールバック関数
def action(cl, info, msg):
    if debug_mode:
        print("get message:")
        print(msg.topic + ":" + str(msg.payload))

    m = json.loads(str(msg.payload))

    if debug_mode:
        print(m)

    id = m['ID']
    if id != my_id:
        print("Not Mine")
        return

    type = m['TYPE']
    if type != 'ACTION':
        print('Not supported:' + type)
        return

    cmd = act_list[m['TARGET']]
    opt = m['OPTION']

    return do_action(cmd, opt)


# センサーデータの読み取り
def get_distance():
    if debug_mode:
        print("get_distance")

    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.3)

    GPIO.output(TRIG, True)
    time.sleep(0.00002)
    #time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        t_low = time.time()

    while GPIO.input(ECHO) == 1:
        t_high = time.time()

    t = t_high - t_low
    distance = t/2 * 340 * 100

    # 450cmが測距限界
    if distance > 450:
        distance = 450

    return distance


# slackへのメッセージ送信
def send_message(token, channel, distance):
    if debug_mode:
        print("send_message:" + token + "," + channel)

    txt = "何かが接近しています。距離 " + str(distance) + " cm"

    client = slack.WebClient(token=token)
    client.chat_postMessage(channel=channel, text=txt)

    if debug_mode:
        print(txt)

    msg = {"STATUS":"OK", "INFO":""}

    return msg

# センサー読み取り準備
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
TRIG = 11
ECHO = 13
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)


"""
# アクション実行の準備
f = open("./config_slack.json", 'r')
act_conf = json.load(f)
f.close()
act_list = {}
cmd_base = act_conf['CMDDIR']
for act in act_conf['ACTIONS']:
    print(act)
    act_list[act['TARGET']] = os.path.join(cmd_base, act['COMMAND'])

if debug_mode:
    print(act_list)


# MQTT Brokerへの接続準備
mqtt_cl = mqtt.Client(protocol=mqtt.MQTTv311)

# サブスクライバの準備
mqtt_cl.on_connect = regist_sub
mqtt_cl.on_message = action
#mqtt_broker_addr="192.168.11.11"
#mqtt_broker_port=1883
#mqtt_broker_addr=str(mqtt_broker_addr)
#mqtt_broker_port=int(mqtt_broker_port)
print("./distance.py159##LIUYI##",mqtt_broker_addr,mqtt_broker_port)
# MQTT Brokerに接続
mqtt_cl.connect(mqtt_broker_addr, port=mqtt_broker_port)


# MQTT処理ループの開始(このループの中で再接続とかもしてくれるとのこと)
mqtt_cl.loop_start()"""

import slack
import os
slack_token='YOUR_SLACK_TOKEN'
client = slack.WebClient(token=slack_token)


# 測距、データ送信を無限ループ
while True:
    try:
        # 測距
        l = get_distance()

        # メッセージ組み立て
        msg = {"ID":my_id, "TYPE":"DISTANCE", "DISTANCE":l}
        print(l)
        msg_txt="(2021.7.30)distance is! "+str(l)+" cm"
        client.chat_postMessage(channel="myserver",text=msg_txt)
        # メッセージ送信
        #mqtt_cl.publish(topic_pub, json.dumps(msg))
        print('sleep: %d' % (interval))
    except KeyboardInterrupt:
        break
    except:
        print(traceback.format_exc())
        pass


    # 指定時間待ち
    if debug_mode:
        print('sleep: %d' % (interval))

    time.sleep(interval)


"""
# MQTT処理ループの終了
mqtt_cl.loop_stop()

# MQTT Brokerからの切断
mqtt_cl.disconnect()"""

