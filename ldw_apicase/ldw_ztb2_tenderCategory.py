#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
招投标2.0接口
"""
import pytest
import json
from common.Request_util import RequestsUtil
from common.params_util import read_caseyaml
class Test_ZTB2:
    #添加招标类类别
    @pytest.mark.parametrize("tenderCategory",(read_caseyaml('ldw_apicase\\case_yaml\\ldw_ztb2_varietyCategory.yaml','varietyCategory')))
    def ops_addtenderCategory(self,tenderCategory):
        name=tenderCategory['name']
        url = tenderCategory['request']['url']
        data = tenderCategory['request']['data']
        headers = tenderCategory['request']['headers']
        method = tenderCategory['request']['method']
        res = RequestsUtil('opsurl').send_requests(method=method, url=url, json=data, headers=headers,name=name,extract=tenderCategory)
        response=json.dumps(res.json(),indent=2, ensure_ascii=False)
        print(response)
if __name__=='__main__':
    pytest.main(['./ldw_ztb2_tenderCategory.py::Test_ZTB2'])