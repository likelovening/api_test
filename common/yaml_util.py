#!/usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
yaml文件读、写、清除的封装方法
by:your old brother always your old brother
"""
import os
import yaml


# from ruamel import yaml

class YamlReader:
    def __init__(self, yamlfile):
        # 判断文件是否存在
        if os.path.exists(yamlfile):
            self.yamlfile = yamlfile
        else:
            raise FileNotFoundError('文件不存在')
        # 默认没有读取过文件
        self._data = {}
        # 默认没有读取过文件
        self._data_all = {}

    # 读取某个字段
    def read_yaml(self, key):
        if not self._data:
            with open(self.yamlfile, mode='r', encoding='utf-8') as f:
                self._data = yaml.safe_load(stream=f)
        if self._data and key in self._data:
            return self._data[key]
        else:
            return ('%s不存在' % key)

    # 读取全部的值
    def read_yamlall(self):
        if not self._data_all:
            with open(self.yamlfile, 'r', encoding='utf-8') as f:
                self._data_all = yaml.load(f, Loader=yaml.FullLoader)
        if self._data_all:
            return self._data_all
        else:
            raise IOError('该文件不存在，无法读取')

# 写入
class YamlWrite:
    def __init__(self, yamlfile):
        # 判断文件是否存在
        if os.path.exists(yamlfile):
            self.yamlfile = yamlfile
        else:
            raise FileNotFoundError('文件不存在')

    # 追加写入：a
    def awrite_yaml(self, data):
        with open(self.yamlfile, 'a', encoding='utf-8') as f:
            yaml.dump(data, stream=f, allow_unicode=True)

    # 覆盖写入：w
    def wwrite_yaml(self, data):
        with open(self.yamlfile, 'w', encoding='utf-8') as f:
            yaml.dump(data, stream=f, allow_unicode=True)

    # yaml文件全部写入
    def yaml_allwrite(self, data):
        # 若不存在，则追加写入
        # if YamlReader(self.yamlfile).read_yaml(key):
        if '不存在' in YamlReader(self.yamlfile).read_yaml(data):
            with open(self.yamlfile, 'a', encoding='utf-8') as f:
                yaml.dump(data, stream=f, allow_unicode=True)
        # 如果已存在对应的value，则替换为新的value
        else:
            old_data = YamlReader(self.yamlfile).read_yamlall()
            with open(self.yamlfile, 'w', encoding='utf-8') as f:
                yaml.dump(old_data, stream=f, allow_unicode=True)

    # Yaml文件key、value替换、写入
    def yaml_write(self, key, value):
        # 定义写入的值为字典类型
        data = {key:value}
        # 若不存在，则追加写入
        if '不存在' in str(YamlReader(self.yamlfile).read_yaml(key)):
            with open(self.yamlfile, 'a', encoding='utf-8') as f:
                yaml.dump(data, stream=f, allow_unicode=True)
        # 如果已存在对应的value，则替换为新的value
        else:
            old_data = YamlReader(self.yamlfile).read_yamlall()
            # 字典的替换
            old_data[key] = value
            with open(self.yamlfile, 'w', encoding='utf-8') as f:
                yaml.dump(old_data, stream=f, allow_unicode=True)
    # yamlfile:文件路径  key:写入字段的key  value:写入字段的value


# 清空
def clean_yaml(yamlfile):
    with open(yamlfile, mode='w', encoding='utf-8') as  f:
        f.truncate()
