# -*- coding: utf-8 -* 
import http.client # --python3.x
#import httplib --python2.x
import time
import os
def get_webservertime(host):
    conn=http.client.HTTPConnection(host) # --python3.x
    #conn=httplib.HTTPConnection(host) --python2.x
    conn.request("GET", "/")
    r=conn.getresponse()
    #r.getheaders() #获取所有的http头
    ts=  r.getheader('date') #获取http头date部分
    #print(ts)
     
    #将GMT时间转换成TOKYO时间
    ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
    #print(ltime)
    ttime=time.localtime(time.mktime(ltime)+9*60*60)
    #print(ttime)
    dat="%u-%02u-%02u"%(ttime.tm_year,ttime.tm_mon,ttime.tm_mday)
    tm="%02u:%02u:%02u"%(ttime.tm_hour,ttime.tm_min,ttime.tm_sec)
    cur_time = dat+" "+tm
    #print (dat,tm)
    print(cur_time)
    command = "sudo date --s='{}'".format(cur_time)
    #print(command)
    os.system(command)
if __name__ == '__main__':
    try:
        get_webservertime('www.google.com') #参数取决于你可以访问的IP地址，外网情况下可以是外网IP，内网可以是服务器可以访问的IP。可以在树莓派浏览器中输入你要填入的IP，能成功响应的即可使用。
        print("校对成功！！！")
    except:
        print("检查与服务器的网络连接，校对失败！")
