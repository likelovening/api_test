#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
在extract.yaml文件中写入mer_token、ops_token
"""
import pytest
from common.Request_util import RequestsUtil
from common.params_util import read_caseyaml
class  Ldw_Token:
    @pytest.mark.parametrize("get_token", (read_caseyaml('base/ldw_gettoken.yaml','get_token')))
    def ldw_getopstoken(self, get_token):
        # print(get_token)
        name = get_token['name']
        url = get_token['request']['url']
        data = get_token['request']['data']
        headers = get_token['request']['headers']
        method = get_token['request']['method']
        if "ops" in name:
            RequestsUtil('opsurl').send_requests(method=method, url=url, data=data, headers=headers, name=name,
                                                 extract=get_token)
        else:
            RequestsUtil('merurl').send_requests(method=method, url=url, data=data, headers=headers, name=name,
                                                 extract=get_token)
if __name__=='__main__':
    pytest.main(['./ldw_gettoken.py::Ldw_Token'])
