import requests
import json

'''matplotlib.use('Agg') # CUI環境でmatplotlib使いたい場合、指定する
import matplotlib.pyplot as plt'''
#TOKEN = 'xoxb-247578397445-2237502186229-eld4CjB9UBfKCM0t2c5LHNOY'
TOKEN = 'YOUR_SLACK_TOKEN'
CHANNEL = 'myserver'


###############
# 画像送信ここから
###############
files = {'file': open("./yutatest.jpg", 'rb')}
#html_report="x.jpg"

param = {
    'token':TOKEN, 
    'channels':CHANNEL,
    'content':"hhh",
    'filename':"filename",
    'title': "title"
}
#r = requests.post(url="https://slack.com/api/files.upload",params=param, files=files)
requests.post(url="https://slack.com/api/files.upload",data=param,files=files)

#print(r)



