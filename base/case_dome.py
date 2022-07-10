#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
好好看，好好学
by：your old brother
"""
import pytest
from common.params_util import read_caseyaml
from common.Request_util import RequestsUtil
from debug_talk import debugtalk
"""
若有csv数据驱动的用例，使用read_caseyaml读取；
若没有csv数据驱动的用例，都可以用
readall_yaml可以在同一个key下多写几条用例
read_caseyaml一个key下仅有一个数据驱动的用例
"""
@pytest.mark.parametrize("casedata_name",(read_caseyaml('casepath.yaml',"casename")))
@pytest.mark.parametrize("casedata_name",(debugtalk.readall_yaml('casepath.yaml')["casename"]))
def test_dome(casedata_name):
    name=casedata_name['name']
    url=casedata_name['request']['url']
    data=casedata_name['request']['data']
    headers=casedata_name['request']['headers']
    method=casedata_name['request']['method']
    """
    若接口需要提取动态参数，则加上extract参数。赋值是整个用例数据
    若不需要则可不写该参数👇
    data/json根据接口类型传入
    """
    RequestsUtil('dome').send_requests(method=method,url=url,params=data,data=data, json=data,headers=headers,name=name,extract=casedata_name)

if __name__=='__main__':
    pytest.main(['./base.py'])