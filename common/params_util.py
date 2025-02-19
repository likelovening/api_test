#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
封装csv数据驱动
用例中添加csvdatapath
"""
from debug_talk import debugtalk
import csv,json,jsonpath,traceback
from common.logger_util import logs

def read_caseyaml(yamlpath,casename):
    try:
        caseinfo = debugtalk.Read_Yaml(yamlpath,casename)
        if jsonpath.jsonpath(caseinfo, "$..csvdatapath"):
            # for key, value in caseinfo.items():
            new_caseinfo = params_data(*caseinfo)
            return new_caseinfo
        else:
            return caseinfo
    except Exception as e:
        logs.error("读取的yaml数据出错，异常：%s" % str(traceback.format_exc()))

def csv_reader(filepath):
    """
    定义csv文件的分割符为":"
    :param filepath:文件路径
    :return: 返回值类型是列表嵌套列表
    """
    temp_list=[]
    with open(debugtalk.get_Path(filepath), "r", encoding='utf-8') as csv_file:
        data = csv.reader(csv_file,delimiter=":",quoting=csv.QUOTE_NONE)
        #新  获取标题
        #headers=next(data)
        for data_list in data:
            #新  存标题一一对应的key value
            #result=dict(zip(headers,data_list))
            temp_list.append(data_list)
        csv_file.close()
        return temp_list
def params_data(all_casedata):
    """
    :param all_casedata: 用例所有的参数
    :return: 替换CSV数据的入参，包含所有csv的数据
    主要为了替换数据驱动的参数，key和value需固定写法
    """
    try:
        if jsonpath.jsonpath(all_casedata,"$..csvdatapath"):
            str_all_casedata=json.dumps(all_casedata)
            flag=True
            for params_key,params_value in dict(all_casedata["csvdatapath"]).items():
                yamlkey_list=params_key.split("-")
                csv_data=csv_reader(params_value)
                # print(csv_data)
                for csvdata in csv_data:
                    if len(csvdata) !=len(yamlkey_list):
                        flag=False
                        logs.error("需要读取的csv数据格式不正确")
                        break
                new_casedata=[]
                if flag:
                    for x in range(1,len(csv_data)):   #行
                        temp_caseinfo=str_all_casedata
                        for y in range(0,len(csv_data[x])):     #列
                            if csv_data[0][y] == yamlkey_list[y]:
                                key=str(csv_data[0][y])
                                value=str(csv_data[x][y])
                                #数字去除引号
                                if isinstance(csv_data[x][y],int) or isinstance(csv_data[x][y],float):
                                    temp_caseinfo=temp_caseinfo.replace('"$ddt{'+key+'}"',value)
                                else:
                                    temp_caseinfo = temp_caseinfo.replace('$ddt{'+key+'}',value)
                            else:
                                logs.error("csv数据读取出错：yaml中csvdatapath的key不匹配csv文件首行标题")
                        new_casedata.append(json.loads(temp_caseinfo))
                    #新  直接循环替换即可
                    # for csv_data_line in csv_list:
                    #需每次重置下入参 不然没有ddt关键字
                    #     dict_casedata = json.dumps(casedata[0])
                    #     for key, value in csv_data_line.items():
                    #         dict_casedata = dict_casedata.replace('$ddt{' + key + '}', value)
                return new_casedata
        else:
            return all_casedata
    except IOError as e:
        logs.error("Error:".format(str(e)))
        raise