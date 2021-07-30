import sys
import requests
import json
import os
import yaml
import os.path as osp
from collections import Iterable
from threading import Lock


"""注意：对配置的修改会作用于所有的机台, 影响产线生产, 请确认要修改的配置！！！"""


def open_file(fp, *args, **kargs):
    if sys.version_info[0] >= 3:
        kargs['encoding'] = 'utf8'
        return open(fp, *args, **kargs)
    else:
        return open(fp, *args, **kargs)


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
        self.stations_id = None
        # 车间 线别 工序
        self.facility_id = 'test_Modif_ops'
        self.product_line = 'test'
        self.stage = 'cengqian'
        self.headers = None
        self.cfg_yaml = None
        self.local_config = config

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


class ModifOpsConfig(OpsConfigBase):
    def __init__(self, config):
        super(ModifOpsConfig, self).__init__(config)
        try:
            self.uid, self.token = self.login()
        except Exception:
            print('登录ops失败，检查ops地址或者用户名及密码！！')

    def get_stations_id(self):
        """
        获取机台id
        :return:
        """
        station_url = f'http://{self.host}:{self.port}/api/v1/stations/?facility_id={self.facility_id}&stage={self.stage}&product_line={self.product_line}'
        self.headers = {
            'AUTHORIZATION': self.token
        }

        station_res = requests.get(url=station_url, headers=self.headers, timeout=10)
        station_res = json.loads(station_res.text)
        print("station_res['data']",station_res['data'])
        if station_res['data']:
            self.stations_id = station_res['data']


    def get_config_and_modify(self):
        """
        获取机台配置
        :return:
        """
        for station in self.stations_id:
            station_id = station['uid']
            print('station_id', station_id)
            config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host,
                                                                                             port=self.port,
                                                                                             station_uid=station_id,
                                                                                             timeout=10)
            data = {
                'without_config': 'false'
            }
            station_config_res = requests.get(url=config_url, data=data, headers=self.headers)
            station_config_res = station_config_res.json()
            station_config_str = station_config_res['data']['config'].encode('utf-8').decode('unicode_escape')
            # print('station_config_str',station_config_str)
            self.cfg_yaml = yaml.load(station_config_str, Loader=yaml.FullLoader)
            save_path = './config__jiangsu/{}_{}_{}.yaml'.format(station['facility_id'], station['product_line'], station['equipment_id'])
            with open(save_path, 'w') as f:
                yaml.dump(station_config_str, f, allow_unicode=False, indent=4, default_flow_style=False, sort_keys=False)
            # key = self.local_config['opsconfig']['key']
            # value = self.local_config['opsconfig']['value']
            # self.modify_config(key, value, station_id)  # 192.168.3.210:8101

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
        
        # config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host, port=self.port,
        #                                                                                  station_uid=station_id)
        # requests.put(url=config_url, data=dict(config=yaml.dump(self.cfg_yaml), config_desc="修改ops配置"),
        #              headers=self.headers, timeout=10)
        # print("修改{0}机台{1}：{2}配置成功！".format(self.ops_addr, station_id, key))

    def put_config(self, station_id):
        for i in os.listdir('D:/Script/put_config'):
            # with open('')
            config_url = 'http://{host}:{port}/api/v1/stations/{station_uid}/config/'.format(host=self.host, port=self.port,
                                                                                            station_uid=station_id)
            requests.put(url=config_url, data=dict(config=yaml.dump(self.cfg_yaml), config_desc="修改ops配置"),
                        headers=self.headers, timeout=10)
            print("修改{0}机台配置成功！".format(station_id))


class ConfigYaml:
    '''基于Yaml的配置类.'''

    def __init__(self, config_dir):
        self.config_dir = config_dir
        self._cache = None
        self.mutex = Lock()

    def get_config(self, key, defval):
        '''返回配置项的值，如果配置不存在，返回defval.'''
        if self._cache is None:
            with self.mutex:
                self._cache = {}

                fp = self.config_dir
                if os.path.exists(fp):
                    with open_file(fp) as ff:
                        cfg_local = yaml.load(ff, Loader=yaml.FullLoader) or {}
                        self._update_config(cfg_local, self._cache)

        v = self._cache
        for k in key.split('.'):
            if not isinstance(v, Iterable):
                return defval
            if isinstance(v, list):
                v = v[0]
            if k not in v:
                return defval
            v = v[k]

        return v

    def get_plugin_config(self, event, name, def_val):
        '''获取插件配置'''
        cfg = self.get_config('event_plugins_binds', [])
        cfg = [x for x in cfg if x.get('event', '') == event]
        if len(cfg) != 1:
            print('插件%s配置有误，请检查', name)
            return
        cfg = cfg[0]['plugins']
        cfg = [x for x in cfg if x.get('name', '') == name]
        if len(cfg) != 1:
            print('插件%s配置有误，请检查', name)
            return

        cfg = cfg[0]['config']
        if cfg is None:
            return def_val

        # rv = cfg[cfg_path]
        # if rv is None:
        #     msg = '插件 {} 中配置 {} 不存在'.format(self, cfg_path)
        #     print(msg)
        #     return def_val
        return cfg

    def _update_config(self, from_, to_):
        if isinstance(from_, dict) and isinstance(to_, dict):
            for key, val_to in to_.items():
                if key not in from_:
                    continue
                val_from = from_[key]
                if isinstance(val_from, dict) and isinstance(val_to, dict):
                    self._update_config(val_from, val_to)
                else:
                    to_[key] = val_from

            for key, val_from in from_.items():
                if key not in to_:
                    to_[key] = val_from

    def flush(self, file_name):
        '''将配置写入磁盘文件。'''
        with self.mutex:
            fp = osp.join('D:\Script\config__jiangsu_4.0', file_name)

            with open(fp, 'w+') as ffw:
                yaml.dump(self._cache, ffw,
                          indent=4, default_flow_style=False, sort_keys=False, encoding='utf-8')

    def set_config(self, key, val):
        '''设置配置'''
        event, plugin, cfg = key.split('.')
        rv = self.get_plugin_config(event, plugin, "")
        # update the cache
        if self._cache:
            rv[cfg] = val



def modif_template_to_customize(old_config_dir):
    # need customize config
    customize_config_dict = {'camera_station.defect_recipe': 'VIPostprocess.DefectRecipePlugin.defect_recipe',
                             'camera_station.component_recipe': 'VIPostprocess.ComponentRecipePlugin.component_recipe',
                             'camera_station.el_result_dir': 'OutputVIResult.SaveLocalResultPlugin.save_directory',
                             'camera_station.el_tracking_dir': 'NoEvent.WatchDogCameraPlugin.tracking_dir',
                             'camera_station.image_source.flip_col_order': 'NoEvent.CameraStationPlugin.flip_col_order',
                             'camera_station.io.port': 'NoEvent.IO44Plugin.port',
                             'camera_station.pre_process.edge_cut_setting.bottom_left': 'VIPreprocess.ManualComEdgeCutPlugin.bottom_left',
                             'camera_station.pre_process.edge_cut_setting.bottom_right': 'VIPreprocess.ManualComEdgeCutPlugin.bottom_right',
                             'camera_station.pre_process.edge_cut_setting.top_left': 'VIPreprocess.ManualComEdgeCutPlugin.top_left',
                             'camera_station.pre_process.edge_cut_setting.top_right': 'VIPreprocess.ManualComEdgeCutPlugin.top_right'
    }

    old_config_file_list = os.listdir(old_config_dir)
    template_config = ConfigYaml('C:Users/LiuWanpin/Desktop/plugin_config/config__隆基江苏串检.yml')
    for i in old_config_file_list:
        print(i)
        config_path = osp.join(old_config_dir, i)
        config = ConfigYaml(config_path)
        for (customize_old_config, customize_new_config) in customize_config_dict.items():
            customize_config_value = config.get_config(customize_old_config, '')

            # 在site_local中的配置项
            if 'pre_process' in customize_old_config:
                site_config  = ConfigYaml("./site_local/{}.yml".format(i.split('.')[0][8:11]))
                customize_config_value = site_config.get_config(customize_old_config, '')
            print('customize_config_value:', customize_config_value)

            template_config.set_config(customize_new_config, customize_config_value)
        file_name = 'config__' + osp.basename(config.config_dir)
        template_config.flush(file_name)


if __name__ == "__main__":
    local_config = LoadConfig()
    local_list_config = local_config.json['ops_list'][0]
    # for local_config in local_list_config['ops_list']:
    #     ops = ModifOpsConfig(local_config)
    #     ops.get_stations_id()
    #     ops.put_config()

    ops = ModifOpsConfig(local_list_config)
    ops.get_stations_id()
    # ops.put_config('D:/Script/put_config')

        # ops.get_config_and_modify()
    # sec = 10
    # print('{0}秒后关闭控制台！'.format(sec))
    # time.sleep(sec)

    # old_config_dir = "D:/Script/config__jiangsu"
    # modif_template_to_customize(old_config_dir)
