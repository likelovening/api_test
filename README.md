# Ldw_ApiTest
ldw接口测试相关
(1)文件夹
    base文件夹：获取ops/mer的token的用例及方法
    common：封装了request方法、yaml文件读写方法、logging、csv数据驱动
    config：基本的url（ops/mer）
    data：csv数据及上传文件
    ldw_apicase：ldw合同管理测试用例
    ldw_Dome：调试文件夹
    conftest.py:pytest框架的前后置
    debug_talk：随机数、本地路径、各种yaml文件的读写
    extract.yaml:存放提取的数据，token及各种ID
    pytest.ini:pytest的配置文件

(2)用例编写规则：
    一级关键字包含：name，request,validate
    request内必须包含method,url;validate代表断言
    用例的key需是list字典形式，即前面加"-"
    变量定义：${funcname(data)}
    文件上传：{"file": ./filepath.docx}
    **参考base中的case_dome**
  
    
(3)CSV数据驱动参数格式：
    csvdatapath:
        name-name-name:filepath
    引用方法:$ddt{name}

(4)数据提取存放，存在根目录‘extract.yaml’文件中
    - 
    正则提取,使用(.*?)或者（.+?）
    例：mer_token: '"accessToken":"(.*?)"'  
    -
    json提取默认取第一个值,config中配置
    mer_token: '$.data[*].accessToken'  
    flodId: '$..flowId[?(@.poly=="id")][road]'