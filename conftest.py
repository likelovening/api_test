#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
import pytest
import pytest
from common.Request_util import RequestsUtil
from debug_talk import debugtalk
from common.params_util import read_caseyaml
#使用session
# @pytest.fixture(scope='function',autouse=True)
# def ldw_getopstoken():
#     get_token=read_caseyaml('base/ldw_gettoken.yaml','get_token')
#     name=get_token['name']
#     url=get_token['request']['url']
#     data=get_token['request']['data']
#     headers=get_token['request']['headers']
#     method=get_token['request']['method']
#     if "ops" in name:
#         RequestsUtil('opsurl').send_requests(method=method,url=url,data=data, headers=headers,name=name,extract=get_token)
#     else:
#         RequestsUtil('merurl').send_requests(method=method, url=url, data=data, headers=headers,name=name,extract=get_token)
#








#不添加autouse时，默认为false；
@pytest.fixture(scope='function')  # 调用时需在方法中添加标记的方法
def use_fixture():
    print('\n前置方法')
    yield
    print('\n后置方法')

def delsql(user):
    sql="delete from users where usernam={}".format(user)
    print("删除用户%s成功"%sql)
#params,参数化，可将装饰器中的参数传入目标函数。固定用法：request.param
@pytest.fixture(scope='function',params=['小1','小2','小3'])  #三个参数会执行三次
def new_fixture(request):
    return request.param
@pytest.fixture(scope='class',params=['小4'])
def new_fixture01(request):
    delsql(request.param)
    yield request.param     #return和yield都有返回的意思，但yield后面可跟代码，return不行。
    print('后置')
