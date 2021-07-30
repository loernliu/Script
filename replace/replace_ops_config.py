# -*- coding: utf-8 -*-
# @Time : 2021/6/22 18:01
# @contact: 1325738369@qq.com
# @Author : tiannan
# @FileName: replace_ops_config.py
# @Software: PyCharm
import time

import requests
import json
import os
import yaml

"""注意：对配置的修改会作用于所有的机台，请确认要修改的配置！！！"""


class LoadConfig:
    """加载配置"""

    def __init__(self):
        self.json_dir = os.getcwd()
        self.json_path = os.path.join(self.json_dir, "config.json")
        self.json = self.load_json()

    def load_json(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            return cfg
        except json.decoder.JSONDecodeError:
            print('配置文件解码失败，请检查！')


class OpsConfigBase:
    def __init__(self, config):
        self.email = config['login']['email']
        self.password = config['login']['password']
        self.ops_addr = config['login']['ops_addr']
        self.host, self.port = self.ops_addr.split(':')
        self.station_id = None
        self.headers = None
        self.cfg_yaml = None
        self.config = config

    def login(self):
        """
        登录ops
        :return:
        """
        login_url = 'http://{host}:{port}/api/v1/users/tokens/'.format(host=self.host, port=self.port)
        data = {
            'email': self.email,
            'password': self.password
        }
        try:
            login_res = requests.post(url=login_url, data=data)
            login_res = json.loads(login_res.text)
            res_data = login_res['data']
            uid = res_data['uid']
            token = res_data['token']
            return uid, token
        except requests.exceptions.InvalidURL:
            print('ops登录地址无效！')
            return


class TestOpsConfig(OpsConfigBase):
    def __init__(self, config):
        self.config = config['test']
        super(TestOpsConfig, self).__init__(self.config)
        try:
            self.uid, self.token = self.login()
        except:
            print('登录ops失败，检查ops地址或者用户名及密码！！')

    def get_station_id(self):
        """
        获取机台id
        :return:
        """
        station_url = 'http://{host}:{port}/api/v1/stations/'.format(host=self.host, port=self.port)
        self.headers = {
            'AUTHORIZATION': self.token
        }
        parm = {
            'facility_id': self.config['identity']['facility_id'],
            'product_line': self.config['identity']['product_line'],
            'stage': self.config['identity']['stage'],
            'function': self.config['identity']['function'],
            'equipment_id': self.config['identity']['equipment_id']
        }

        station_res = requests.get(url=station_url, headers=self.headers, params=parm, timeout=10)
        station_res = json.loads(station_res.text)
        if station_res['data']:
            self.station_id = station_res['data'][0]['uid']

    def get_config_and_modify(self):
        """
        获取机台配置
        :return:
        """
        config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host,
                                                                                         port=self.port,
                                                                                         station_uid=self.station_id,
                                                                                         timeout=10)
        data = {
            'without_config': 'true'
        }
        station_config_res = requests.get(url=config_url, data=data, headers=self.headers)
        station_config_res = json.loads(station_config_res.text)
        station_config_str = station_config_res['data']['config']
        self.cfg_yaml = yaml.load(station_config_str, Loader=yaml.FullLoader)
        key = self.config['opsconfig']['key']
        value = self.config['opsconfig']['value']
        ops.modify_config(key, value)  # 192.168.3.210:8101

    def modify_config(self, key, value):
        """
        修改机台配置
        :param key:
        :param value:
        :return:
        """
        if self.cfg_yaml:
            v = self.cfg_yaml
            for k in key.split('.')[:-1]:
                if k not in v:
                    v[k] = {}
                v = v[k]
            v[key.split('.')[-1]] = value
        config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host, port=self.port,
                                                                                         station_uid=self.station_id)
        requests.put(url=config_url, data=dict(config=yaml.dump(self.cfg_yaml), config_desc="修改ops配置"),
                     headers=self.headers, timeout=10)
        print("修改{0}机台{1}：{2}配置成功！".format(self.ops_addr, self.station_id, key))


class ModifOpsConfig(OpsConfigBase):
    def __init__(self, config):
        super(ModifOpsConfig, self).__init__(config)
        try:
            self.uid, self.token = self.login()
        except:
            print('登录ops失败，检查ops地址或者用户名及密码！！')
        self.stations_id = None

    def get_stations_id(self):
        """
        获取机台id
        :return:
        """
        station_url = 'http://{host}:{port}/api/v1/stations/'.format(host=self.host, port=self.port)
        self.headers = {
            'AUTHORIZATION': self.token
        }

        station_res = requests.get(url=station_url, headers=self.headers, timeout=10)
        station_res = json.loads(station_res.text)
        if station_res['data']:
            self.stations_id = station_res['data']

    def get_config_and_modify(self):
        """
        获取机台配置
        :return:
        """
        for station in self.stations_id:
            station_id = station['uid']
            config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host,
                                                                                             port=self.port,
                                                                                             station_uid=station_id,
                                                                                             timeout=10)
            data = {
                'without_config': 'true'
            }
            station_config_res = requests.get(url=config_url, data=data, headers=self.headers)
            station_config_res = json.loads(station_config_res.text)
            station_config_str = station_config_res['data']['config']
            self.cfg_yaml = yaml.load(station_config_str, Loader=yaml.FullLoader)
            key = self.config['opsconfig']['key']
            value = self.config['opsconfig']['value']
            self.modify_config(key, value, station_id)  # 192.168.3.210:8101

    def modify_config(self, key, value, station_id):
        """
        修改机台配置
        :param key:
        :param value:
        :return:
        """
        if self.cfg_yaml:
            v = self.cfg_yaml
            for k in key.split('.')[:-1]:
                if k not in v:
                    v[k] = {}
                v = v[k]
            v[key.split('.')[-1]] = value
        config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host, port=self.port,
                                                                                         station_uid=station_id)
        requests.put(url=config_url, data=dict(config=yaml.dump(self.cfg_yaml), config_desc="修改ops配置"),
                     headers=self.headers, timeout=10)
        print("修改{0}机台{1}：{2}配置成功！".format(self.ops_addr, station_id, key))


if __name__ == "__main__":
    local_config = LoadConfig()
    local_list_config = local_config.json
    if local_list_config['test']['enable'].lower() == 'true':
        ops = TestOpsConfig(local_list_config)
        ops.get_station_id()
        ops.get_config_and_modify()
    else:
        for local_config in local_list_config['ops_list']:
            ops = ModifOpsConfig(local_config)
            ops.get_stations_id()
            ops.get_config_and_modify()
    sec = 10
    print('{0}秒后关闭控制台！'.format(sec))
    time.sleep(sec)
