#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
在extract.yaml文件中写入mer_token、ops_token
"""
import pytest,allure
from common.Request_util import RequestsUtil
from common.params_util import read_caseyaml
from debug_talk import debugtalk
class  Ldw_Token:
    @pytest.mark.parametrize("get_token", (read_caseyaml('base/ldw_gettoken.yaml', 'get_token')))
    def ldw_getopstoken(self, get_token):
        name = get_token['name']
        url = get_token['request']['url']
        data = get_token['request']['data']
        headers = get_token['request']['headers']
        method = get_token['request']['method']
        # 根据配置选择不同测试环境
        EnvironM = debugtalk.read_configyaml("EnvironMent", "Chose")
        if "ops" in name:
            allure.dynamic.title("Ops_Token信息获取")
            RequestsUtil('{}_ops_url'.format(EnvironM)).send_requests(method=method, url=url, data=data,
                                                                      headers=headers, name=name,
                                                                      extract=get_token)
        else:
            allure.dynamic.title("Mer_Token信息获取")
            RequestsUtil('{}_mer_url'.format(EnvironM)).send_requests(method=method, url=url, data=data,
                                                                      headers=headers, name=name,
                                                                      extract=get_token)
if __name__=='__main__':
    pytest.main(['./ldw_gettoken.py::Ldw_Token'])
