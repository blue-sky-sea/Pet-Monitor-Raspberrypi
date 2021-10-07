#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import traceback
import MyServer.mystorage as MyStorage
import MyServer.common as MyCom



# 動作設定
#debug_mode = True
debug_mode = False
use_BME280 = True
use_DHT11 = False


if use_DHT11:
    import DHT11.dht11_func as MySensor
elif use_BME280:
    import BME280.bme280_func as MySensor


# config.jsonを読み、パラメータを取得
MyCom.load_config('./config.json')
my_id = MyCom.id()
storage_service = MyCom.storage()
interval = MyCom.interval()
app_id = MyCom.app_id()


# ストレージ・サービスのURLを設定
#print("sensor.py: storage_service=",storage_service)
#MyStorage.set_url(storage_service)

# データ取得、送信を無限ループ
while True:
    try:
        # データを読み込む
        d = MySensor.get_data()
        #if debug_mode:
         #   print(d)
        # ファイル名を組み立てる(デフォルト)
        path = MyCom.monitor_sensor_path()
        if debug_mode:
            print(sys._getframe().f_code.co_name+':path='+path)
        print("data:",d)
        # データを保存
        #print("sensor.py: ",path,d)
        #res = MyStorage.save_data(path, d)
        #print("[sensor.py]res=",res)
        #if res != 200:
           #print('Failed to save data.')

    except KeyboardInterrupt:
       break
    except:
       print(traceback.format_exc())
       pass


# 指定時間待ち
    if debug_mode:
        print('sleep: %d' % (interval))

    time.sleep(interval)
