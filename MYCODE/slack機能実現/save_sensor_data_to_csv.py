#!/usr/bin/env python
# -*- coding: utf-8 -*-
debug_mode=False
import time
import sys
import traceback
import datetime


import pandas as pd
#sudo apt-get install python3-pandas

#import pandas as pd
#in raspberry PI
#sudo apt-get install python3-pandas
#sudo pip3 install -U pandas
#sudo apt-get install python-dev libatlas-base-dev

import MyServer.common as MyCom
#import jsonsaver  as JsonSaver
import BME280.bme280_func as BMESensor

# config.jsonを読み、パラメータを取得
MyCom.load_config('./config.json')


#--------------------------------------------
savepath="./data/"
interval=1 #every interval get data from sensors
SAVE_N=60*5 #every SAVE_N times get-data operation,save data to json
Name = "liuyi"
#--------------------------------------------



import json
def save_tocsv(path,filename,data_object):
    #filename="test1.json"
    filepath=path+filename
    #input("see...")
    with open(filepath,'w') as f:
        for i in data_object:
            f.write(str(i)+'\n')
    #print(json_str)  
    #df_data.to_csv(filepath)
    return True

def makeJSON(t,p,h,time):
	dp = {"temperature":t, "pressure":p, "humidity":h,"nowtime":time}
	d = json.JSONEncoder().encode(dp)
	return d  
    
environment_data_t = []
environment_data_p = []
environment_data_h = []
environment_data_time = []
json_data = []
n=0

data_list=[]
i=0


while True:
    try:
        # データを読み込む
        t,p,h = BMESensor.get_data()
        now_time = datetime.datetime.now()
        environment_data_t.extend([t])
        environment_data_p.extend([p])
        environment_data_h.extend([h])
        environment_data_time.extend([str(now_time)])
        
        n=n+1
        
        # データを保存       
        if(n==SAVE_N):
            df_environment = pd.DataFrame(columns=['Time','temperature','pressure','humidity'])
            #every 60sec save data to csv
            df_environment['Time']=environment_data_time
            df_environment['temperature']=environment_data_t
            df_environment['pressure']=environment_data_p
            df_environment['humidity']=environment_data_h
            
            date = str(datetime.datetime.now().strftime('%Y-%m-%d'))
            path = savepath
            
            filename = date+Name+str(i)+".csv"
            #print(environment_data_time)
            df_environment.to_csv(path+filename)
            print("save to",path,filename,"success")
            
            i=i+1
            n=0
            environment_data_t.clear()
            environment_data_p.clear()
            environment_data_h.clear()
            environment_data_time.clear()
            
               
                
        #environment_data
        #print(res)
    except KeyboardInterrupt:
       break
    except:
       print(traceback.format_exc())
       pass


# 指定時間待ち
    if debug_mode:
        print('sleep: %d' % (interval))

    time.sleep(interval)
