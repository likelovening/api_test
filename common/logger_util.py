#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
import logging,time
from logging.handlers import RotatingFileHandler
from debug_talk import debugtalk
class Log_uilt:
    def __init__(self):
        self.log=logging.getLogger(debugtalk.read_configyaml("logger","name"))
        self.log.setLevel(debugtalk.read_configyaml("logger","level"))

    def create_log(self):
        #设置log地址及log名称规则
        logname=("{}\\{}.log").format(debugtalk.get_Path("log"),time.strftime("%Y-%m-%d",time.localtime()))
        #控制器流log格式
        consloe_fmt=logging.Formatter('%(asctime)s-->%(filename)s-->%(levelname)s-->%(message)s')
        #文本log格式
        file_fmt=logging.Formatter("%(lineno)s行  %(asctime)s 运行:%(filename)s %(funcName)s %(levelname)s message:%(message)s")
        #通用fmt
        fmt=debugtalk.read_configyaml("logger","format")
        user_fmt=logging.Formatter(fmt)
        if not self.log.handlers:
            #配置流输出
            consloe_handler=logging.StreamHandler()
            consloe_handler.setLevel(logging.INFO)
            consloe_handler.setFormatter(user_fmt)

            #配置文本格式，日志回滚
            file_Handler = RotatingFileHandler(logname,maxBytes=3*1024,mode='a', encoding='utf-8')
            file_Handler.setLevel(logging.DEBUG)
            file_Handler.setFormatter(user_fmt)

            self.log.addHandler(file_Handler)
            self.log.addHandler(consloe_handler)
        return self.log



def error_log(message):
    Log_uilt().create_log().error(message)
    raise Exception(message)
# def logs(message):
#     Log_uilt().create_log().info(message)
logs=Log_uilt().create_log()

