#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
封装了获取随机数、目录path、读写extract、config等yaml文件的方法
by:your old brother
"""
import random, json, datetime,pymysql
from common.yaml_util import YamlReader, YamlWrite
import os, base64,requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as pks
from urllib.parse import quote_plus
from pathlib import Path


class DebugTalk:
    #Url加密
    def Url_encoded(self,str):
        Category=quote_plus(str)
        return Category
    #Url解密
    def Url_decoded(self,str_incoded):
        return requests.utils.quote(str_incoded)

    # 读取txt文件
    def read_fairmeeting_notice(self, name):
        name = name.encode('utf-8').decode("unicode_escape")
        data_path = debugtalk.get_Path("data\\{}".format(name))
        with open(data_path, 'r', encoding='gbk', errors='ignore') as f:
            data = f.read()
        return data

    # 包含日期的递增数
    def degrees_num(self):
        if "不存在" in self.read_extractyaml("order_num"):
            self.write_ExtractYaml("order_num", "01")
        today_data = (datetime.datetime.now()).strftime("%Y%m%d")
        if "不存在" in self.read_extractyaml("today_data"):
            self.write_ExtractYaml("today_data", today_data)
        elif today_data != self.read_extractyaml("today_data"):
            self.write_ExtractYaml("today_data", today_data)
            self.write_ExtractYaml("order_num", "01")
        old_num = self.read_extractyaml("order_num")
        num = self.read_extractyaml("today_data")
        degrees_num = num + "00" + str(old_num)
        new_num = int(old_num) + 1
        self.write_ExtractYaml("old_num", str(degrees_num))
        self.write_ExtractYaml("order_num", str(new_num))
        return degrees_num

    # 获取当前时间+num(mins)
    def timeInfo(self, num):
        num = int(num)
        more_time = (datetime.datetime.now() + datetime.timedelta(minutes=num)).strftime("%Y-%m-%d %H:%M")
        return more_time

    # 获取当前完整时间+num(mins)
    def timeInfo_00(self, num):
        num = int(num)
        more_time = (datetime.datetime.now() + datetime.timedelta(minutes=num)).strftime("%Y-%m-%d %H:%M:00")
        return more_time

    # 获取当前完整时间+num(hour)
    def timeInfo_Hours(self, num):
        num = int(num)
        more_time = (datetime.datetime.now() + datetime.timedelta(hours=num)).strftime("%Y-%m-%d %H:%M:00")
        return more_time

    # 登录\支付密码加密
    def test_password_rsa(self, password):
        base64_str = base64.b64encode(password.encode())
        #测试环境加密
        publickey_path = debugtalk.get_Path('data/RSA_publickey.pem')
        # 生产环境密码加密
        # publickey_path = debugtalk.get_Path('data/RSA_publickey(dev).pem')
        with open(publickey_path, 'rb')as f:
            publickey = f.read()
        key = RSA.importKey(publickey)
        cipher = pks.new(key)
        rsa_str = base64.b64encode(cipher.encrypt(base64_str)).decode()
        decond_password = base64.b64encode(rsa_str.encode())
        return decond_password.decode()
    #登录账号加密
    def test_username_rsa(self,username):
        #测试环境加密
        # publickey_path = debugtalk.get_Path('data/RSA_publickey.pem')
        # 生产环境密码加密
        publickey_path = debugtalk.get_Path('data/RSA_publickey(dev).pem')
        with open(publickey_path, 'rb')as f:
            publickey = f.read()
        key = RSA.importKey(publickey)
        cipher = pks.new(key)
        user=bytes(username,encoding='utf8')
        rsa_str = base64.b64encode(cipher.encrypt(user)).decode()
        decond_username = base64.b64encode(rsa_str.encode())
        return decond_username.decode('utf-8')
    # 生成随机数
    def get_random(self, min, max):
        random_num=random.randint(int(min), int(max))
        self.write_ExtractYaml("random_num",random_num)
        return random_num

    # 获取项目根目录路径
    def get_Path(self, path):
        """
        parts的判断是层级的判断，本地层级小的修改方法类
        """
        try:
            curpath = os.path.dirname(os.path.realpath(__file__))
            #获取文件绝对路径
            current_file = Path(__file__).resolve()
            #切片文件路径并存到list中
            parts=current_file.parts
            for num_length in range(len(parts)):
                content_path=curpath[:curpath.find(parts[num_length]) + len(parts[num_length])]
                actual_path=os.path.join(str(content_path), path)
                if os.path.exists(actual_path):
                    return actual_path if current_file.is_absolute() else None
        except:
            IOError("路径获取错误")

    # 根据保证金比例获取首次保证金支付金额
    def pay_payBondScale(self):
        payBondScale = float(self.read_extractyaml("payBondScale"))
        actualReceipt = float(self.read_extractyaml("actualReceipt"))
        payBondScale = float(payBondScale * actualReceipt / 100)
        return payBondScale

    # 获取箱号
    def get_Gen_ContainerNo(self):
        basic_character = "0123456789A?BCDEFGHIJK?LMNOPQRSTU?VWXYZ"
        letter = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sum = 0
        # 随机取四位大写字母list
        letter_list = random.sample(letter, 4)
        # list转str
        letter_str = "".join(letter_list)
        # 随机取6位字母
        RandomData = random.randint(100000, 999999)
        # 将字母和数字连接起来
        ContainerId_list = letter_str.upper() + "{}".format(RandomData)
        # 循环获取字母数字对应的数
        for i in range(0, len(ContainerId_list)):
            # 循环字母表
            for upper_num in range(0, len(basic_character)):
                if ContainerId_list[i] == basic_character[upper_num]:
                    sum += upper_num * (2 ** i)
        # 检验位计算
        check_digit = sum % 11 % 10
        # 拼接箱号
        ContainerNo = str(letter_str) + str(RandomData) + str(check_digit)
        return ContainerNo
    #获取粮贸商城单托箱号
    def get_singlecontainids_from_mysql(self):
        DBHOST = '10.37.103.33'
        DBUSER = 'sunjianing'
        DBPASS = 'ldw123456'
        DBNAME = 'ContainsID_Test'
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME, charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute("select * from contains_test where is_inuse=0 AND isdouble=0")
            self.containid=cursor.fetchone()
            cursor.execute('update  contains_test set is_inuse=1 where id=(%s)'%repr(self.containid[0]))
            db.commit()
            debugtalk.write_ExtractYaml("Containid_in_mysql_id", self.containid[0])
        except:
            IOError("获取箱号失败")
        cursor.close()
        db.close()
        return self.containid[1]

    #获取粮贸商城双托箱号
    def get_dualcontainids_from_mysql(self):
        DBHOST = '10.37.103.33'
        DBUSER = 'sunjianing'
        DBPASS = 'ldw123456'
        DBNAME = 'ContainsID_Test'
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME, charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute("select * from contains_test where is_inuse=0 AND isdouble=1")
            self.containid = cursor.fetchone()
            cursor.execute('update  contains_test set is_inuse=1 where id=(%s)' % repr(self.containid[0]))
            db.commit()
            debugtalk.write_ExtractYaml("Containid_in_mysql_id",self.containid[0])
        except:
            IOError("获取箱号失败")
        cursor.close()
        db.close()
        return self.containid[1]

    #获取对应箱号的重量
    def get_containerWeight(self):
        DBHOST = '10.37.103.33'
        DBUSER = 'sunjianing'
        DBPASS = 'ldw123456'
        DBNAME = 'ContainsID_Test'
        db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME, charset='utf8')
        cursor = db.cursor()
        try:
            cursor.execute("select weightNum from contains_test where id=(%s)"% repr(debugtalk.read_extractyaml("Containid_in_mysql_id")))
            self.weightNum = cursor.fetchone()
            db.commit()
        except:
            IOError("获取重量失败")
        cursor.close()
        db.close()
        return self.weightNum[0]
    # 选择所有数据的前几个以str输出
    def output_str(self, data_name, num):
        num=int(num)
        try:
            read_data = self.read_extractyaml(data_name)
            all_data_list = list(read_data.split(","))
            output_data = all_data_list[:num]
            output_str=",".join(output_data)
        except:
            read_data = self.read_extractyaml(data_name)
            all_data_list = list(read_data.split(",", num))
            output_data = all_data_list[:num]
            output_str = ",".join(output_data)
        return output_str

    # 选择所有数据的前几个以list输出
    def output_list(self, data_name, num):
        try:
            read_data = self.read_extractyaml(data_name)
            all_data_list = read_data.split(",")
            output_data = all_data_list[:num]
        except:
            read_data = self.read_extractyaml(data_name)
            all_data_list = read_data.split(",", num)
            output_data = all_data_list[:num]
        return output_data

    #商城计算保证金
    def bondAmount_Num(self):
        price=self.read_extractyaml("actualPrice")
        num=self.read_extractyaml("buyNumber")
        payBondScale=self.read_extractyaml("payBondScale")
        return float(price)*float(num)*float(payBondScale)/100
    # 写入config.yaml文件
    def write_ConfigYaml(self, key, value):
        if key:
            if value:
                yamlpath = self.get_Path('config\\config.yaml')
                YamlWrite(yamlpath).yaml_write(key, value)
        else:
            raise ("写入的key为空")

    # 写入extract.yaml文件
    def write_ExtractYaml(self, key, value):
        if key:
            if value:
                yamlpath = self.get_Path('extract.yaml')
                YamlWrite(yamlpath).yaml_write(key, value)
        else:
            raise ("写入的key为空")

    # 调试用，写入token.yaml
    def write_tokenyaml(self, key, value):
        yamlpath = self.get_Path('ldw_Dome\\token.yaml')
        YamlWrite(yamlpath).yaml_write(key, value)

    # 读取本地路径yaml文件
    def readall_yaml(self, datapath):
        realpath = self.get_Path(datapath)
        return YamlReader(realpath).read_yamlall()

    # 读取某个yaml文件中key用例(params_util)
    def Read_Yaml(self, Yamlpath, casename):
        realpath = self.get_Path(Yamlpath)
        data=YamlReader(realpath).read_yamlall()[casename]
        return data
    # 读取extract_yaml文件某个值
    def read_extractyaml(self, nodename):
        yamlpath = self.get_Path('extract.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)

    # 读取config.yaml文件某个值
    def read_configyaml(self, nodename, second=None):
        yamlpath = self.get_Path('config\\config.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)[second]

    # 读取tokenyaml文件的值
    def read_tokenyaml(self, nodename):
        yamlpath = self.get_Path('ldw_Dome\\token.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)

    # yaml转换json
    def yaml_to_json(self, filepath):
        yamldata = self.readall_yaml(filepath)
        jsondata = json.dumps(yamldata, ensure_ascii=False)
        return jsondata


debugtalk = DebugTalk()
