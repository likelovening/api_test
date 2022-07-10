#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
封装了获取随机数、目录path、读写extract、config等yaml文件的方法
by:your old brother
"""
import random
from common.yaml_util import YamlReader,YamlWrite
import os
class DebugTalk:
    #生成随机数
    def get_random(self,min,max):
        return random.randint(int(min),int(max))
    #获取项目根目录路径
    def get_Path(self,path):
        """
        若项目路径修改，请同步修改写死的路径即：ldw_apitest
        """
        curpath=os.path.dirname(os.path.realpath(__file__))
        rootpath=curpath[:curpath.find("ldw_apitest")+len("ldw_apitest\\")]
        dataPath=os.path.join(rootpath,path)
        return dataPath

    #写入extract.yaml文件
    def write_ExtractYaml(self,key,value):
        if key:
            if value:
                yamlpath=debugtalk.get_Path('extract.yaml')
                YamlWrite(yamlpath).yaml_write(key,value)
        else:
            raise ("写入的key为空")
    #调试用，写入token.yaml
    def write_tokenyaml(self,key,value):
        yamlpath = debugtalk.get_Path('ldw_Dome\\token.yaml')
        YamlWrite(yamlpath).yaml_write(key, value)

    # 读取本地路径yaml文件
    def readall_yaml(sefl, datapath):
        realpath=debugtalk.get_Path(datapath)
        return YamlReader(realpath).read_yamlall()

    #读取某个yaml文件中key用例(params_util)
    def Read_Yaml(self,Yamlpath,casename):
        realpath=debugtalk.get_Path(Yamlpath)
        return YamlReader(realpath).read_yamlall()[casename]



    # 读取extract_yaml文件某个值
    def read_extractyaml(self, nodename):
        yamlpath=debugtalk.get_Path('extract.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)

    # 读取config.yaml文件某个值
    def read_configyaml(self, nodename,second=None):
        yamlpath=debugtalk.get_Path('config\\config.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)[second]

    #读取tokenyaml文件的值
    def read_tokenyaml(self, nodename):
        yamlpath=debugtalk.get_Path('ldw_Dome\\token.yaml')
        return YamlReader(yamlpath).read_yaml(nodename)
    #写入临时文件

debugtalk=DebugTalk()