# -*- coding: utf-8 -*-

import time
import sys
import os
import traceback
import json
import subprocess
import paramiko
import scp

import datetime

class VK(object):
    __VK_IP = '127.0.0.1'
    __VK_PORT = 22
    __VK_USER = 'pi'
    __VK_PASSWD = 'raspberry'

    def __init__(self, ip, port, user, passwd):
        self.__VK_IP = ip
        self.__VK_PORT = port
        self.__VK_USER = user
        self.__VK_PASSWD = passwd

    # SSH接続する
    def __ssh_connect(self, host, port, user, passwd):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=user, password=passwd, port=port, timeout=20, look_for_keys=False)

        return ssh

    # SSH切断する
    def __ssh_disconnect(self, ssh):
        ssh.close()


    # scpでファイル転送する(ローカル->リモート)
    def __put_file(self, ssh, f_file, t_file):
        with scp.SCPClient(ssh.get_transport()) as rcp:
            rcp.put(f_file, t_file)

        return True


    # scpでファイル転送する(リモート->ローカル)
    def __get_file(self, ssh, f_file, t_file):
        with scp.SCPClient(ssh.get_transport()) as rcp:
            rcp.get(f_file, t_file)

        return True


    # sshでコマンドを実行する
    def __remote_exec(self, ssh, cmd):
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = ''
        err = ''
        for o in stdout:
            out = out + o
        for e in stderr:
            err = err + e

        return out, err


    # コマンドを実行して、標準出力を結果として返す
    def __do_cmd(self, ssh, cmd, opt):
        # 実行コマンドを組み立てる
        c = cmd +' ' + ' '.join(opt)

        # 実行
        o, e = self.__remote_exec(ssh, c)

        return o, e


    def __copy_file(self, ssh, f_file, t_file):
        # ホストとファイルを取得
        f_h = t_h = None
        if f_file.find(':') > 0:
            f_h, f_f = f_file.split(':')
        else:
            f_f = f_file

        if t_file.find(':') > 0:
            t_h, t_f = t_file.split(':')
        else:
            t_f = t_file

        if t_h != None and f_h != None:
            print('リモート間のコピーはできません:(' + f_h + ' -> ' + t_h + ')')
            return False

        if t_h == None and f_h == None:
            print('ローカル間のコピーはできません')
            return False

        # ディレクトリ取得
        d = os.path.dirname(t_f)

        try:
            # ディレクトリ作成&ファイルコピー
            if t_h != None:
                if d != '' and d != '.':
                    # リモートにディレクトリ作成
                    self.__do_cmd(ssh, 'mkdir', ['-p', d])
                # コピー
                self.__put_file(ssh, f_f, t_f)

            else:
                if d != '' and d != '.':
                    # ローカルにディレクトリ作成
                    os.makedirs(d)
                # コピー
                self.__get_file(ssh, f_f, t_f)
        except Exception as e:
            print('!!ERROE!!')
            print(e)
            return False

        return True


    def vk_put_file(self, f_file, t_file):
        # SSH準備
        ssh = self.__ssh_connect(self.__VK_IP, self.__VK_PORT, self.__VK_USER, self.__VK_PASSWD)
        # コピー
        res = self.__copy_file(ssh, f_file, self.__VK_IP + ':' + t_file)
        # SSH切断
        self.__ssh_disconnect(ssh)

        return res

    def vk_get_file(self, f_file, t_file):
        # SSH準備
        ssh = self.__ssh_connect(self.__VK_IP, self.__VK_PORT, self.__VK_USER, self.__VK_PASSWD)
        # コピー
        res = self.__copy_file(ssh, self.__VK_IP + ':' + f_file, t_file)
        # SSH切断
        self.__ssh_disconnect(ssh)

        return res


    # Vision Kitのコマンドを実行して結果を受け取る
    def vk_exec(self, cmd, opt):
        # SSH準備
        ssh = self.__ssh_connect(self.__VK_IP, self.__VK_PORT, self.__VK_USER, self.__VK_PASSWD)

        # コマンド実行
        o, e = self.__do_cmd(ssh, cmd, opt)

        # SSH切断
        self.__ssh_disconnect(ssh)

        if len(e) != 0:
            print("ERROR:" + e)

        return o
    # 画像認識realtime
    def vk_raspistill(self,out_filepath):
        #print(out_filepath.split('/')[-1])
        filename = out_filepath.split('/')[-1]
        #print("filename:",filename)
        
        if out_filepath != None:
            o_file = os.path.normpath(os.path.join('data/', filename))
        else:
            o_file = '_out.jpg'
        #print("o_file:",o_file)
        
        out = self.vk_exec('raspistill',['-o '+ "data/"+filename])
        print("###exec raspistill func###")
        
        pic = os.path.join('data/', filename)
        
        t_file = os.path.normpath(os.path.join('data/', filename))


        # 認識結果画像を取得
        #print("o_file, o_pic,out_filepath",o_file, out_filepath,o_pic)
        if out_filepath != None:
            res = self.vk_get_file(o_file, filename)
        
        # 削除
        res = self.vk_exec('rm -f', [t_file])
        return out
    
    
    # 画像認識
    def vk_recog_image(self, pic, o_pic):
        # os.path.join()では/が入っているとそこがrootになってしまうので、/で分解して結果のリストを分解して渡す
        t_file = os.path.normpath(os.path.join('CQ/MyServer/VK/', *pic.split('/')))
        if o_pic != None:
            o_file = os.path.normpath(os.path.join('CQ/MyServer/VK/', *o_pic.split('/')))
        else:
            o_file = '_out.jpg'
            
        # コピー
        res = self.vk_put_file(pic, t_file)
        
        # 認識
        out = self.vk_exec('~/AIY-voice-kit-python/src/examples/vision/object_detection.py', ['--input '+ t_file, '--output ' + o_file])

        # 認識結果画像を取得
        if o_pic != None:
            res = self.vk_get_file(o_file, o_pic)
        
        # 削除
        res = self.vk_exec('rm -f', [t_file])

        return out
    # stream  boxing
    def vk_box_stream(self,picname):
        #vk_output_file = "human.jpg"
        #vk_output_file = os.path.normpath(os.path.join('data/',picname ))#faces.jpg
        #pi_output_file = os.path.normpath(os.path.join('',picname ))
        
        # 認識
        out = self.vk_exec('~/AIY-voice-kit-python/src/examples/vision/face_detection_camera.py', [])

        # 認識結果画像を取得
        #if pi_output_file != None:
            #res = self.vk_get_file(vk_output_file, pi_output_file)
        
        # 削除
        #res = self.vk_exec('rm -f', [vk_output_file])
        
        return out
     #   face boxing one time
    def vk_box_face(self,picname):
        vk_output_file = "human.jpg"
        #vk_output_file = os.path.normpath(os.path.join('data/',picname ))#faces.jpg
        pi_output_file = os.path.normpath(os.path.join('',picname ))
        
        # 認識
        out = self.vk_exec('~/AIY-voice-kit-python/src/examples/vision/face_detection_rectangle.py', [])

        # 認識結果画像を取得
        if pi_output_file != None:
            res = self.vk_get_file(vk_output_file, pi_output_file)
        
        # 削除
        res = self.vk_exec('rm -f', [vk_output_file])
        
        return out
    # 画像認識
    def vk_recog_face(self,picname):
        vk_output_file = "faces.jpg"
        #vk_output_file = os.path.normpath(os.path.join('data/',picname ))#faces.jpg
        pi_output_file = os.path.normpath(os.path.join('',picname ))
        
        # 認識
        out = self.vk_exec('~/AIY-voice-kit-python/src/examples/vision/face_camera_trigger.py', [])

        # 認識結果画像を取得
        if pi_output_file != None:
            res = self.vk_get_file(vk_output_file, pi_output_file)
        
        # 削除
        res = self.vk_exec('rm -f', [vk_output_file])
        
        return out


    # 猫が写っているか判定
    '''
    object_detection.pyの出力は以下の形式。
    Object #0: kind=CAT(2), score=0.871475, bbox=(75, 166, 485, 351)
    Object #1: kind=CAT(2), score=0.557364, bbox=(329, 144, 266, 329)
    kind=に、PERSON,CAT,DOGのように認識したオブジェクトが表示される。
    認識されない場合は何も出力されない。
    '''
    def vk_is_cat(self, pic, result):
        # 認識処理
        res = self.vk_recog_image(pic, result)

        # 猫かどうか確認
        if 'kind=CAT' in res:
            return True
        else:
            return False
    def vk_is_human(self,pic,result):
        # 認識処理
        res = self.vk_recog_image(pic, result)
        print(res)
        # humanかどうか確認
        if 'kind=PERSON' in res:
            return True
        else:
            return False
        
    def vk_human_detect(self,interval):
        n=0
        N=10
        while(True):
            now_time = str(datetime.datetime.now().strftime("%H{H}%M{M}%S{S}").format(H="h",M="m",S="s"))
            #print(now_time)
            #filename
            picname = now_time+"test.jpg"

            #if there is a human face,photograph it and save img to pi_output_file
            out=vk.vk_recog_face(picname)
            
            pi_output_file = os.path.normpath(os.path.join('',picname ))
            
            #test its human or not
            res=True
            #res = vk.vk_is_human(pi_output_file, './'+now_time+ 'result.jpg')
            if(res==True):
                print("is human!",res)
                time.sleep(interval)
            else:
                print("is not human!",res)
                time.sleep(interval)
            if(n==N):
                break

# コマンドラインモード、テストモード
if __name__ == "__main__":
    #vk = VK('raspberrypi.local', 22, 'pi', 'raspberry')
    vk = VK('192.168.11.4', 22, 'pi', 'raspberry')
    #vk = VK('192.168.11.4', 22, 'pi', '123456')
    print("--"*20)
    print("-----------connect to visionkit--------------")
    print(vars(vk))
    print("---------visionkit connect success!-------------")
    print("--"*20)
    
    """
    picname="yutatest.jpg"
    out=vk.vk_recog_face(picname)
    print(out)"""
    #vk.vk_human_detect(1)
    #vk.vk_human_detect(interval=0.1)
    picname="human.jpg"
    vk.vk_box_face(picname)
    vk_box_stream
    #res = vk.vk_is_human()
    #print(res)
    
    #res = vk.vk_is_cat('./people.jpg', './people_result.jpg')
    #print(res)
    """res = vk.vk_is_cat('./cats.jpg', './cats_result.jpg')
    print(res)
    res = vk.vk_is_cat('./cat2.jpg', './cat2_result.jpg')
    print(res)
    res = vk.vk_is_cat('./human.jpg', './human_result.jpg')
    print(res)
    res = vk.vk_is_cat('./dog.jpg', './dog_result.jpg')
    print(res)
    res = vk.vk_is_cat('./city.jpg', './city_result.jpg')
    print(res)"""
