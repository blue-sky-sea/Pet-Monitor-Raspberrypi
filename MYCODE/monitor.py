#!/usr/bin/env python
# -*- coding: utf-8 -*-
import visionkit 
import datetime

import traceback
import json
import subprocess
import paramiko
import scp


import time
import sys
import traceback
import os
import json
import subprocess
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import slack

#debug_mode = True

debug_mode = False
import os,sys
retval = os.getcwd()
print(retval)

# アクション実行
def do_action(cmd, opt):
    if debug_mode:
        print("do_action:" + cmd + " " + opt)
    ret = subprocess.call([cmd, opt])
    return ret
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


# センサー読み取り準備
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
TRIG = 11
ECHO = 13
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)


"""
# アクション実行の準備
f = open("./distance_config.json", 'r')
act_conf = json.load(f)
f.close()
act_list = {}
cmd_base = act_conf['CMDDIR']
for act in act_conf['ACTIONS']:
    print(act)
    act_list[act['TARGET']] = os.path.join(cmd_base, act['COMMAND'])
"""
# 動作設定
#debug_mode = True
#debug_mode = False
use_BME280 = True
use_DHT11 = False


if use_DHT11:
    import DHT11.dht11_func as MySensor
elif use_BME280:
    import BME280.bme280_func as MySensor
# データ取得、送信を無限ループ

slack_token='HERE YOUR TOKEN'
client = slack.WebClient(token=slack_token)

#os.chdir()
my_id="MIZUKI"
import requests
import json
def slack_file_send(filepath):
    TOKEN = slack_token
    CHANNEL = 'myserver'
    ###############
    # 画像送信ここから
    ###############
    files = {'file': open(filepath, 'rb')}
    #html_report="x.jpg"

    param = {
        'token':TOKEN, 
        'channels':CHANNEL,
        'content':"hhh",
        'filename':"filename",
        'title': "title"
    }
    #r = requests.post(url="https://slack.com/api/files.share",params=param, files=files)
    requests.post(url="https://slack.com/api/files.upload",params=param,files=files)
    
def vk_human_detect(interval):  
    now_time = str(datetime.datetime.now().strftime("%H{H}%M{M}%S{S}").format(H="h",M="m",S="s"))        
    picname = now_time+"test.jpg"

    #if there is a human face,photograph it and save img to pi_output_file
    out=vk.vk_recog_face(picname)
    # データを読み込む
    # 測距
    l = get_distance()
    t,p,h  = MySensor.get_data()
    
    pi_output_file = os.path.normpath(os.path.join('',picname ))
        
    #test its human or not
    #res = vk.vk_is_human(pi_output_file, './'+now_time+ 'result.jpg')
    res=True
    if(res==True):
        print("is human!",res)
        # メッセージ組み立て
        msg = {"ID":my_id,"TYPE":"SENSORDATA", "DISTANCE":l,"TEM":t,"PRES":p,"HUMI":h}
        #print(l)
        msg_txt="(2021.8.18)sensor data! "+str(msg)
        client.chat_postMessage(channel="myserver",text=msg_txt)
        
        #import slack

        filepath='./'+now_time+ 'test.jpg'
        #time.sleep(5)
        #client = slack.WebClient(token=slack_token)
        #r = client.files_upload(file=filepath,channel='myserver')
        #print(filepath,r)

        
        TOKEN = slack_token
        CHANNEL = 'myserver'

        ###############
        # 画像送信ここから
        ###############
        files = {'file': open(filepath, 'rb')}
        #html_report="x.jpg"

        param = {
            'token':TOKEN, 
            'channels':CHANNEL,
            'content':"hhh",
            'filename':"filename",
            'title': "title"
        }
        #r = requests.post(url="https://slack.com/api/files.upload",params=param, files=files)
        r=requests.post(url="https://slack.com/api/files.upload",data=param,files=files)
        print(filepath,r)
        
        #delete file
        osr = os.remove(filepath)
        print("filepath deleted!",filepath,osr)
        
        #vk.vk_exec('rm -f')
        time.sleep(interval)
    else:
        print("is not human!",res)
        time.sleep(interval)
     

vk = visionkit.VK('192.168.11.4', 22, 'pi', 'raspberry')
print(vars(vk))

while(True):
    try:
        vk_human_detect(10)
    except KeyboardInterrupt:
        break
    except:
        print(traceback.format_exc())
        pass
