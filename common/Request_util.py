#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
requests方法的封装、动态数据的提取、写入，log获取
by:your old brother
"""
import re, jsonpath
import requests
import json, time, traceback
from debug_talk import debugtalk
from loguru import logger
from common.logger_util import logs
from xpinyin import Pinyin


class RequestsUtil():
    # 使用session关联
    session = requests.session()

    def __init__(self, second):
        # 读取config.yaml文件中的基础路经
        self.base_url = debugtalk.read_configyaml('base_url', second)

    def get_contractMaxNo_re(self, response):
        """
        :param response: 接口返回值
        :return: 合同最大可用量从小到大排序
        """
        contractMaxNo_list = []
        #获取粮源池符合要求的grainList；核算单位及配送方式
        check_dataAccountingUnitName = debugtalk.read_configyaml("SaleContract", "dataAccountingUnitName")
        check_deliveryType = debugtalk.read_configyaml("SaleContract", "deliveryType")
        grain_list = jsonpath.jsonpath(response,
                                       '$..[?(@.dataAccountingUnitName=="{}" && @.deliveryType=="{}")].grainListVoList'.format(
                                           check_dataAccountingUnitName, check_deliveryType))
        grainId_list=re.findall(r"'grainId': '(\w+)'", str(grain_list))
        str_grainId_list=",".join(grainId_list)
        debugtalk.write_ExtractYaml("grainId_list",str_grainId_list)
        # 获取接口返回值种所有的重量
        contractMaxNo_re = re.findall(r"'contractMaxNo': (\d+\.\d+)", str(grain_list))
        # 筛选类型和编码一致的粮贸合同
        for i in range(len(contractMaxNo_re)):
            try:
                # 提取类型大写和名称拼音
                packageType_info = jsonpath.jsonpath(response,
                                                     '$..grainListVoList[?(@.contractMaxNo=={})].packageType'.format(
                                                         contractMaxNo_re[i]))
                packageTypeName_info = jsonpath.jsonpath(response,
                                                         '$..grainListVoList[?(@.contractMaxNo=={})].packageTypeName'.format(
                                                             contractMaxNo_re[i]))
                # 核对类型大写与拼音是否一致
                if packageType_info[0] == Pinyin().get_initials(packageTypeName_info[0], ""):
                    contractMaxNo_list.append(contractMaxNo_re[i])
            except:
                logs.info("合同中存在类型编号或名称为空的情况")
        # 返回排序后的重量list
        return sorted(contractMaxNo_list, key=lambda x: float(x))

    def get_jsonpath(self, response, code_info, a):
        """
        :param response: 接口返回值
        :param code_info: json提取的字段名称
        :param a: json返回的第一个值
        :return: 提取对应重量的code_info的值
        """
        return jsonpath.jsonpath(response,
                                 '$..grainListVoList[?(@.contractMaxNo=={})].{}'.format(
                                     self.get_contractMaxNo_re(response)[a],
                                     code_info))

    def get_extract_data(self, casedata, response):
        """
        封装提取动态参数，yaml文件内需包含extract一级关键字
        调用断言，调用响应log
        :param casedata: 用例yaml内容
        :param response: 接口返回结果
        :return:
        """
        num = debugtalk.read_configyaml("extract", 'num')
        if jsonpath.jsonpath(casedata, '$.validate') and casedata["validate"] != None:
            yq_result = casedata["validate"]
            sj_result = response.json()
            s_code = jsonpath.jsonpath(response.json(), 'code')[0]
            # 调用断言
            self.validata_result(yq_result, sj_result, s_code)
        if casedata:
            casedata_key = casedata.keys()
            if 'extract' in casedata_key and casedata['extract'] != None:
                for key, value in casedata['extract'].items():
                    # 正则提取
                    if "(.*?)" in value or "(.+?)" in value:
                        # 匹配结果中的正则语句
                        extract_value = re.search(value, response.text)
                        # 匹配所有结果
                        all_extract_value = re.findall(value, response.text)
                        regex_value = ""
                        # 写入第一个匹配的值
                        if extract_value.group(num):
                            debugtalk.write_ExtractYaml(key, extract_value.group(num))
                        # 写入所有匹配的值
                        if all_extract_value != None:
                            for i in all_extract_value:
                                if i != all_extract_value[-1]:
                                    regex_value = regex_value + str(i) + ","
                                else:
                                    regex_value = regex_value + str(i)
                            debugtalk.write_ExtractYaml("all_" + key, regex_value)
                        else:
                            logs.info('提取{}值时为空'.format(key))
                    elif "$" in value:
                        try:
                            # jsonpath提取
                            result_json = response.json()
                            extract_value = jsonpath.jsonpath(result_json, value)
                            # 获取全部的json匹配值
                            str_extract_value = ""
                            if isinstance(extract_value, list) and extract_value[num - 1]:
                                for i in extract_value:
                                    if i != extract_value[-1]:
                                        str_extract_value = str_extract_value + str(i) + ","
                                    else:
                                        str_extract_value = str_extract_value + str(i)
                                # 同时写入第一和全部提取的数据
                                debugtalk.write_ExtractYaml("all_" + key, str_extract_value)
                                debugtalk.write_ExtractYaml(key, str(extract_value[num - 1]))
                            else:
                                logs.info('提取{}值时为空'.format(key))
                        except IOError as e:
                            raise ('接口返回类型异常，无法使用json提取')
                    elif "@" in value:
                        try:
                            grain_dict = {}
                            begin_num=0
                            result_json = response.json()
                            result_dict = json.loads(response.text)
                            #先获取合同量排序
                            contractMaxNo_list = self.get_contractMaxNo_re(result_json)
                            #判断最大重量对应的粮源池关联号有没有在池中
                            str_grainId= self.get_jsonpath(result_json, "grainId", len(contractMaxNo_list)-1)[begin_num]
                            if str_grainId not in debugtalk.read_extractyaml("grainId_list"):
                                begin_num+=1
                            # 反向迭代reversed
                            for i in reversed(range(len(contractMaxNo_list))):
                                grain_dict["contractMaxNo"] = contractMaxNo_list[i]
                                # 获取所有接口需要用的信息，为空则停止本次循环开始下一次循环，全部不为空则跳出本次循环
                                grain_dict["deliveryCode"] = self.get_jsonpath(result_json, "deliveryCode", i)[begin_num]
                                grain_dict["grainId"] = self.get_jsonpath(result_json, "grainId", i)[begin_num]
                                grain_dict["deliveryDetailAddr"] =self.get_jsonpath(result_json, "deliveryDetailAddr", i)[begin_num]
                                grain_dict["deliveryAddr"] = self.get_jsonpath(result_json, "deliveryAddr", i)[begin_num]
                                grain_dict["grainEndTime"] = self.get_jsonpath(result_json, "grainEndTime", i)[begin_num]
                                grain_dict["grainBeginTime"] = self.get_jsonpath(result_json, "grainBeginTime", i)[begin_num]
                                grain_dict["deliveryEndTime"] = self.get_jsonpath(result_json, "deliveryEndTime", i)[begin_num]
                                grain_dict["deliveryBeginTime"] = \
                                self.get_jsonpath(result_json, "deliveryBeginTime", i)[begin_num]
                                grain_dict["contractPrice"] = self.get_jsonpath(result_json, "contractPrice", i)[begin_num]
                                # 判断所有的值非空
                                if "" in grain_dict.values():
                                    continue
                                else:
                                    break
                            # 获取合同最大可用量对应的粮源池ID
                            Contract_Id_Maxno = {}
                            for record in result_dict['data']['records']:
                                #判断粮源池不为空，且选择条件
                                if record.get('grainListVoList') != None:
                                    for grain in record['grainListVoList']:
                                        #获取所有的粮源池编号
                                        data_ContractId = record.get('dataContractId')
                                        #获取所有的粮源池关联号
                                        data_grainId=str(grain.get('grainId'))
                                        #获取全部粮源池关联号对应的编号
                                        Contract_Id_Maxno[data_grainId] = data_ContractId
                                else:
                                    logs.info("粮源池信息均为空")
                            #拿到最大重量对应的粮源池关联号对应的粮源池编号
                            grain_dict["contractId"] = Contract_Id_Maxno.get(grain_dict["grainId"])
                            for key, value in grain_dict.items():
                                debugtalk.write_ExtractYaml(key, value)
                        except:
                            logs.info("粮源池信息返回不完整，无法自动获取粮源池信息")
            else:
                pass

    def replace_value(self, data):
        """
        函数作用于替换动态参数，使用于send_requests内
        :param data: 需要替换的值value
        :return:返回替换后的动态参数
        """
        if data:
            # 保存数据格式，以便后续还原
            data_type = type(data)
            # 字典和列表统一更改为json字符串
            if isinstance(data, dict) or isinstance(data, list):
                str_data = json.dumps(data)
            # 其他类型更改为字符串类型
            else:
                str_data = str(data)
            # 替换带有${}格式的数据(即动态数据)
            for yee in range(1, str_data.count('${') + 1):
                # 需要替换的数据范围
                if "${" in str_data and "}" in str_data:
                    # 获取第一个${下标的索引
                    startIndex = str(str_data).find("${")
                    # 截取第一个${后面的值存为新值
                    new_data = str(str_data)[int(startIndex):]
                    # 获取第一个}的索引
                    endIndex = str(new_data).find("}") + startIndex
                    # 获得需要替换的值
                    oldValue = str(str_data)[int(startIndex):int(endIndex) + 1]
                    # 查找方法名
                    func_name = str(oldValue)[2:str(oldValue).find('(')]
                    # 查找数据名
                    args_data = str(oldValue)[str(oldValue).index("(") + 1:str(oldValue).index(")")]
                    # 为空则直接调用方法
                    if args_data != "":
                        # 多个数据判断
                        if "," in args_data:
                            args_data = args_data.split(",")
                            # getattr方法，字符串调用方法
                            new_value = getattr(debugtalk, func_name)(*args_data)
                        else:
                            new_value = getattr(debugtalk, func_name)(args_data)
                    else:
                        new_value = getattr(debugtalk, func_name)()
                    # 数字的话 去除“”
                    if isinstance(new_data, int) or isinstance(new_data, float):
                        str_data = str_data.replace("" + str(oldValue) + "", str(new_value), 1)
                    else:
                        str_data = str_data.replace(oldValue, str(new_value), 1)
            # 还原数据类型
            if isinstance(data, dict) or isinstance(data, list):
                data = json.loads(str_data, strict=False)
            else:
                data = data_type(str_data)
        return data

    def validata_result(self, yq_result, sj_result, status_code):
        """
        断言判断，在提取值中使用；因为俩者所用参数一致；统一在send_request中调用
        :param yq_result: 预期结果；list类型
        :param sj_result: 实际结果;dict类型
        :param status_code:实际结果中的业务code
        :return:
        """
        try:
            flag = 0
            if yq_result and isinstance(yq_result, list):
                for yq in yq_result:
                    for validate_key, validate_value in dict(yq).items():
                        if validate_key == "equals":
                            for key, value in dict(validate_value).items():
                                if key == "code":
                                    if int(status_code) != int(value):
                                        flag = +1
                                        logs.error("断言失败，返回的code码{}不等于{}".format(status_code, value))
                                else:
                                    sj_code_0 = jsonpath.jsonpath(sj_result, '$.' + key + '')
                                    sj_code_1 = jsonpath.jsonpath(sj_result, '$.data.' + key + '')
                                    if sj_code_0:
                                        if value not in sj_code_0:
                                            flag = +1
                                            logs.error("{}断言失败，实际结果:{}，预期结果:{}".format(key, sj_code_0, value))
                                    elif sj_code_1:
                                        if value not in sj_code_1:
                                            flag = +1
                                            logs.error("{}断言失败，实际结果:{}，预期结果:{}".format(key, sj_code_1, value))
                                    else:
                                        flag = +1
                                        logs.error("断言异常，实际结果中没有{}".format(key))
                        elif validate_key == "contains":
                            for contains_value in validate_value:
                                if contains_value not in json.dumps(sj_result):
                                    flag = +1
                                    logs.error("断言失败，实际结果中不包含{}".format(validate_value))
                        else:
                            logs.error("呼叫your old brother,这种断言暂不支持")
            assert int(flag) == 0

        except Exception as e:
            logs.error("断言失败，异常信息：{}".format(str(traceback.format_exc(e))))

    def _request_log(self, url, method, name, **kwargs):
        """
        使用loguru库，封装请求头log
        :param url: 请求地址
        :param method: 请求方法
        :param name: 请求名称
        :param kwargs: header、params、json、data
        :return:
        """
        track = logger.add(
            ("{}\\{}.log").format(debugtalk.get_Path("log"), time.strftime("%Y-%m-%d", time.localtime())),
            level="INFO", encoding="utf-8", enqueue=True, rotation="10MB")
        if name:
            logger.info("接口名称: {}".format(name, indent=4, ensure_ascii=False))
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

    def _response_log(self, response):
        """
        返回log设定
        :param response: 接口返回值
        :return: 提取接口返回code等信息
        """
        # 配置返回参数的log
        track = logger.add(
            ("{}\\{}.log").format(debugtalk.get_Path("log"), time.strftime("%Y-%m-%d", time.localtime())),
            level="INFO", encoding="utf-8", enqueue=True, rotation="10MB")
        res = json.dumps(response.json(), ensure_ascii=False)
        response_code = json.loads(res, strict=False)["code"]
        response_success = json.loads(res, strict=False)["success"]
        response_msg = json.loads(res, strict=False)["msg"]
        if response_code != "200":
            logs.error("接口报错，报错信息为：{}".format(response_msg))
        try:
            logger.info("接口返回code：%s" % response_code)
            logger.info("接口返回success：{}".format(response_success, ensure_ascii=False))
            logger.info("接口返回msg：{}".format(response_msg, ensure_ascii=False))
            # logger.info("接口测试通过")
        except Exception as e:
            logger.error('系统错误：{}'.format(e))
        logger.remove(track)

    def send_requests(self, method, url, name=None, extract=None, **kwargs):
        """
        封装基本请求方式，包含动态参数获取、替换、log打印
        :param method: 接口请求方式
        :param url: 接口请求地址
        :param name: 接口请求名称（log封装使用）
        :param extract:接口需要提取的值（get_extract_data）
        :param kwargs:
        :return:
        """
        # 请求方式处理
        method = str(method).lower()
        # url拼接
        url = self.base_url + self.replace_value(url)
        # 如果有动态参数需替换
        for key, value in kwargs.items():
            if key in ["params", 'data', 'json', 'headers']:
                # 将替换后的值赋予原key
                kwargs[key] = self.replace_value(value)
            # 文件上传单独处理
            elif key == 'files':
                if value != None:
                    for file_key, file_value in value.items():
                        value[file_key] = open(debugtalk.get_Path(file_value), 'rb')
                else:
                    pass
        self._request_log(url, method, name, **kwargs)
        response = RequestsUtil.session.request(method, url, **kwargs)
        self._response_log(response)
        self.get_extract_data(extract, response)
        return response
