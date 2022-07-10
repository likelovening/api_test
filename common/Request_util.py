#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
request方法的封装、动态数据的提取、写入，log获取
by:your old brother
"""
import re,jsonpath
import requests
import json,time,traceback
from debug_talk import debugtalk
from loguru import logger
from common.logger_util import logs

class RequestsUtil:
    #使用session关联
    session=requests.session()
    def __init__(self,second):
        #读取config.yaml文件中的基础路经
        self.base_url=debugtalk.read_configyaml('base_url',second)

    def get_extract_data(self, casedata, response):
        """
        封装提取动态参数，yaml文件内需包含extract一级关键字
        调用断言，调用响应log
        :param casedata: 用例yaml内容
        :param response: 接口返回结果
        :return:
        """
        num=debugtalk.read_configyaml("extract",'num')
        yq_result=casedata["validate"]
        sj_result=response.json()
        status_code=response.status_code
        #调用断言
        self.validata_result(yq_result,sj_result,status_code)
        if casedata:
            casedata_key = casedata.keys()
            if 'extract' in casedata_key:
                for key, value in casedata['extract'].items():
                    # 正则提取
                    if "(.*?)" in value or "(.+?)" in value:
                        # 匹配结果中的正则语句
                        extract_value = re.search(value, response.text)
                        if extract_value.group(num):
                            debugtalk.write_ExtractYaml(key, extract_value.group(num))
                        else:
                            logs.info('提取{}值时为空'.format(key))
                    else:
                        try:
                            # jsonpath提取
                            result_json = response.json()
                            extract_value = jsonpath.jsonpath(result_json, value)
                            if extract_value[num-1]:
                                debugtalk.write_ExtractYaml(key, extract_value[num-1])
                            else:
                                logs.info('提取{}值时为空'.format(key))
                        except IOError as e:
                            raise('接口返回类型异常，无法使用json提取')
            else:
                pass
        track = logger.add(
            ("{}\\{}.log").format(debugtalk.get_Path("log"), time.strftime("%Y-%m-%d", time.localtime())),
            level="INFO", encoding="utf-8", enqueue=True, rotation="10MB")
        res = json.dumps(response.json(), ensure_ascii=False)
        try:
            logger.info("接口返回code：%s" % json.loads(res)["code"])
            logger.info("接口返回success：{}".format(json.loads(res)["success"], ensure_ascii=False))
            logger.info("接口返回msg：{}".format(json.loads(res)["msg"], ensure_ascii=False))
            logger.info("接口测试通过")
        except Exception as e:
            logger.error('系统错误：{}'.format(e))
        logger.remove(track)
        time.sleep(0.1)

    def replace_value(self,data):
        """
        函数作用于替换动态参数，使用于send_requests内
        :param data: 需要替换的值value
        :return:返回替换后的动态参数
        """
        if data:
            #保存数据格式，以便后续还原
            data_type=type(data)
            #字典和列表统一更改为json字符串
            if isinstance(data,dict) or isinstance(data,list):
                str_data=json.dumps(data)
            #其他类型更改为字符串类型
            else:
                str_data=str(data)
            #替换带有${}格式的数据(即动态数据)
            for yee in range(1,str_data.count('${')+1):
                #需要替换的数据范围
                if  "${" in str_data and "}" in str_data:
                    # 获取第一个${下标的索引
                    startIndex = str(str_data).find("${")
                    # 截取第一个${后面的值存为新值
                    new_data = str(str_data)[int(startIndex):]
                    # 获取第一个}的索引
                    endIndex = str(new_data).find("}") + startIndex
                    # 获得需要替换的值
                    oldValue = str(str_data)[int(startIndex):int(endIndex) + 1]
                    #查找方法名
                    func_name=str(oldValue)[2:str(oldValue).find('(')]
                    #查找数据名
                    args_data=str(oldValue)[str(oldValue).index("(")+1:str(oldValue).index(")")]
                    #为空则直接调用方法
                    if args_data!="":
                        #多个数据判断
                        if "," in args_data:
                            args_data=args_data.split(",")
                            #getattr方法，字符串调用方法
                            new_value=getattr(debugtalk,func_name)(*args_data)
                        else:
                            new_value=getattr(debugtalk,func_name)(args_data)
                    else:
                        new_value=getattr(debugtalk,func_name)
                    #数字的话 去除“”
                    if  isinstance(new_data,int) or isinstance(new_data,float):
                        str_data=str_data.replace(""+str(oldValue)+"",str(new_value))
                    else:
                        str_data=str_data.replace(oldValue,str(new_value))
            #还原数据类型
            if isinstance(data,dict) or isinstance(data,list):
                data=json.loads(str_data)
            else:
                data=data_type(str_data)
        return data

    def validata_result(self,yq_result,sj_result,status_code):
        """
        断言判断，在提取值中使用；因为俩者所用参数一致；统一在send_request中调用
        :param yq_result: 预期结果；list类型
        :param sj_result: 实际结果;dict类型
        :param status_code:
        :return:
        """
        try:
            flag=0
            if yq_result and isinstance(yq_result, list):
                for yq in yq_result:
                    for validate_key, validate_value in dict(yq).items():
                        #print(validate_key)
                        if validate_key == "equals":
                            for key, value in dict(validate_value).items():
                                #print(key)
                                #print("value:{}".format(value))
                                if key == "code":
                                    if status_code != int(value):
                                        flag = +1
                                        logs.error("断言失败，返回的code码不等于{}".format(value))
                                else:
                                    sj_code = jsonpath.jsonpath(sj_result, '$.'+key+'')
                                    #print("实际结果中的{}值".format(sj_code))
                                    #value = str(value).lower()
                                    #print("预期结果中的值：{}".format(value))
                                    if sj_code:
                                        #print(value)
                                        if value not in sj_code:
                                            flag = +1
                                            logs.error("{}断言失败，实际结果:{}，预期结果:{}".format(key,sj_code,value))
                                    else:
                                        flag = +1
                                        logs.error("断言异常，实际结果中没有{}".format(key))
                        elif validate_key == "contains":
                            #print("预期中contains的{}值".format(validate_value))
                            for contains_value in validate_value:
                                if contains_value not in json.dumps(sj_result):
                                    flag = +1
                                    logs.error("断言失败，实际结果中不包含{}".format(validate_value))
                        else:
                            logs.error("呼叫your old brother,这种断言暂不支持")
            assert int(flag)==0
        except Exception as e:
            logs.error("断言失败，异常信息：{}".format(str(traceback.format_exc(e))))

    def _request_log(self,url,method,name,**kwargs):
        """
        使用loguru库，封装请求头log
        :param url: 请求地址
        :param method: 请求方法
        :param name: 请求名称
        :param kwargs: header、params、json、data
        :return:
        """
        track=logger.add(("{}\\{}.log").format(debugtalk.get_Path("log"), time.strftime("%Y-%m-%d", time.localtime())),
                   level="INFO", encoding="utf-8", enqueue=True, rotation="10MB")
        if name:
            logger.info("接口名称: {}".format(name,indent=4,ensure_ascii=False))
        logger.info("接口请求地址: {}".format(url))
        logger.info("接口请求方式: {}".format(method))
        if "headers" in kwargs:
            logger.info("接口请求头: {}".format(kwargs["headers"], indent=4, ensure_ascii=False))
        if "params" in kwargs:
            logger.info("接口请求 params 参数: {}".format(kwargs["params"], indent=4, ensure_ascii=False))
        if "data" in kwargs:
            logger.info("接口请求体 data 参数: {}".format(kwargs["data"], indent=4, ensure_ascii=False))
        if "json" in kwargs:
            logger.info("接口请求体 json 参数: {}".format(kwargs["json"], indent=4, ensure_ascii=False))
        logger.remove(track)

    def send_requests(self,method,url,name=None,extract=None,**kwargs):
        """
        封装基本请求方式，包含动态参数获取、替换、log打印
        :param method: 接口请求方式
        :param url: 接口请求地址
        :param name: 接口请求名称（log封装使用）
        :param extract:接口需要提取的值（get_extract_data）
        :param kwargs:
        :return:
        """
        #请求方式处理
        method = str(method).lower()
        #url拼接
        url=self.base_url+self.replace_value(url)
        #如果有动态参数需替换
        for key,value in kwargs.items():
            if key in ["params",'data','json','headers']:
                #将替换后的值赋予原key
                kwargs[key]=self.replace_value(value)
            #文件上传单独处理
            elif key=='files':
                for file_key,file_value in value.items():
                    value[file_key]=open(file_value,'rb')
        self._request_log(url,method,name,**kwargs)
        response=RequestsUtil.session.request(method,url,**kwargs)
        #self._response_log(response)
        self.get_extract_data(extract,response)
        return response


