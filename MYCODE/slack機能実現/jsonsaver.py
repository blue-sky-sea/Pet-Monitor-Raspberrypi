#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
import datetime
import json
import sys

#
# ストレージ・サービスにアクセスするライブラリ
#



debug_mode = True
#api_url = "http://127.0.0.1:4001/storage/"
api_url = "http://192.168.11.10:3000/storage/"


# 初期化
def set_url(url):
    global api_url
    api_url = url
    return


# ファイル一覧を取得する
# オプションはファイルパス
def list(path=''):
    # JSONモードで 一覧取得、指定フォルダは以下のファイル一覧を取得する
    # いずれプリフィックスや時間範囲での取得もしたい。。。
    try:
        resp = requests.get(api_url+path, params={'format':'json'})
        flist = resp.json()['files']
    except requests.exceptions.TooManyRedirects:
        flist = []
        if debug_mode:
            print(sys._getframe().f_code.co_name+":There is no data. redirection over")

    except Exception as e:
        flist = None
        if debug_mode:
            print(sys._getframe().f_code.co_name+":get failed")
            print(e)

    return flist


# ファイル保存
def save_file(name, path):
    try:
        print("[mystorage.py]:api_url=",api_url)
        resp = requests.post(api_url, files={'file':(path, open(path, 'rb'))}, data={'name': name})
        r = resp.status_code

    except Exception as e:
        r = 500
        if debug_mode:
            print(sys._getframe().f_code.co_name+":post failed")
            print(e)

    return r


# データ保存
def save_data(name, data):
    try:
        print("[mystorage.py]:api_url=",api_url," name=",name," data.json=",data)
        resp = requests.post(api_url, files={'file':('data.json', data)}, data={'name': name})
        r = resp.status_code
    except Exception as e:
        r = 500
        if debug_mode:
            print(sys._getframe().f_code.co_name+":post failed")
            print(e)

    return r
    

# データ取得
def get(name, param=''):
    try:
        resp = requests.get(api_url+name)
        data = resp.content

    except Exception as e:
        data = None
        if debug_mode:
            print(sys._getframe().f_code.co_name+":get failed")
            print(e)

    return data


# 削除
def delete(name):
    try:
        resp = requests.delete(api_url+name)
        r = resp.status_code

    except Exception as e:
        r = 500
        if debug_mode:
            print(sys._getframe().f_code.co_name+":post failed")
            print(e)

    return r
        


# リネーム
def rename(oldname, newname):
    try:
        resp = requests.put(api_url+oldname, params={'rename':newname})
        r = resp.status_code

    except Exception as e:
        r = 500
        if debug_mode:
            print(sys._getframe().f_code.co_name+":put failed")
            print(e)

    return r
    




# コマンドラインモード、テストモード
if __name__ == "__main__":

    # save
    print('save file')
    res = save_file('a.jpeg', './test.jpg')
    print(res)

    # list
    print('list all')
    res = list()
    print(res)
    if res != None:
        for f in res:
            print(f)

    print('list under DATADIR')
    res = list('DATADIR')
    print(res)
    if res != None:
        for f in res:
            print(f)

    # get 
    res = get('a.jpeg', '')

    # save local file
    if res != None:
        f = open('./a.jpg', 'wb')
        f.write(res)
        f.close()


    # rename
    print('rename')
    res = rename('a.jpeg', 'a.jpg')
    print(res)

    # delete
    print('delete no file')
    res = delete('p.jpeg')
    print(res)
    print('delete file')
    res = delete('a.jpg')
    print(res)



    # save
    print('save data')
    res = save_data('bb.json','{"temp":20, "pres":1000}')
    print(res)

