import requests
import json
import pandas as pd
import numpy as np
import matplotlib

'''matplotlib.use('Agg') # CUI環境でmatplotlib使いたい場合、指定する
import matplotlib.pyplot as plt'''

TOKEN = 'YOUR_SLACK_TOKEN'
CHANNEL = 'myserver'

#####################################
# 画像を生成する例、アップロードするだけなら不要
#####################################

'''# データ読み込む
data = pd.read_table(
    "/path/to/data/input.tsv", #なんかtsv/csv読み込むサンプル
    header=-1, 
    names=("date","value")
)
# 軸の基準になるとこ
data.index = pd.to_datetime(data.iloc[:,0])
data.plot()
# 保存するよ
plt.savefig('figure.png')'''

###############
# 画像送信ここから
###############
files = {'file': open("x.jpg", 'rb')}
#html_report="x.jpg"

param = {
    'token':TOKEN, 
    'channels':CHANNEL,
    'content':"hhh",
    'filename':"filename",
    'title': "title"
}
#r = requests.post(url="https://slack.com/api/files.share",params=param, files=files)
requests.post(url="https://slack.com/api/files.upload",data=param,files=files)

print(r)


