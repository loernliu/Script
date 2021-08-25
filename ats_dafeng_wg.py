'''
MES 客户端
'''
from cmath import pi
import os
import json
import logging
import copy
import time
import yaml
import requests
from PyQt5.QtWidgets import QApplication
from scipy.misc import face
from zeep import Client
from zeep.transports import Transport
from zeep.cache import InMemoryCache
from config import config, site
from plugins.hp_plugin import HPPluginBase
from plugins.mes.process_mes_data import MesDataProcess
from plugins.mes.mes_login_dlg import MesLoginDialog
from plugins.mes.image_transfer import image_transfer_for_mes
from plugins.hp_event import HPEventType
from el_lib.hp_error import HPErrorType, ErrStatus


class MesAtsDaFengWG(HPPluginBase, MesDataProcess):
    '''MES对象'''

    def __init__(self, *args, **kwargs):
        HPPluginBase.__init__(self, *args, **kwargs)
        MesDataProcess.__init__(self)

        self.wsdl = self.get_config('wsdl', 'http://172.26.8.64:8888/mycim2/services/JobManagementWebService?wsdl')
        self.client = None
        self._get_defect_label_map()
        self.connect_qsignal(HPEventType.AppStarted, self.dialog)

    def _get_defect_label_map(self):
        el_defects = config.get_config("mes_defects", [])
        defect_label_map = dict()
        for item in el_defects:
            defect_label_map[item.get("code")] = item.get("label")
        self.defect_label_map = defect_label_map
        logging.info("defect_label_map: %s" % self.defect_label_map)

    def connect(self):
        cache = InMemoryCache(timeout=None)
        cache_file = os.path.join(os.path.abspath(os.getcwd()), 'plugins', 'mes', 'mes_cache', 'schemas.xmlsoap.org.xml')
        with open(cache_file, 'rb') as f:
            cache.add('http://schemas.xmlsoap.org/soap/encoding/', f.read())
        transport = Transport(cache=cache, timeout=3)

        logging.info("MES 对象尝试连接")
        for ii in range(3):
            try:
                self.client = Client(wsdl=self.wsdl, transport=transport)
                self.client.transport.session.verify = False
                break
            except requests.exceptions.RequestException:
                logging.exception('MES 连接失败。')
                self.client = None
                self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=True))
            time.sleep(1)

    def dialog(self, data):
        if not self.enabled:
            return
        self.connect()
        stage = site.get_config('identity.stage', 'cengqian')
        if stage == 'cengqian':
            app = QApplication([])
            dlg = MesLoginDialog(self.login)
            dlg.show()
            app.exec_()

    def login(self, user_name, password, facility_id):
        '''登录检查.
        MES 接口 login方法说明
        用户权限验证方法login方法：string login(String userName, String password, String facilityId)
        方法参数：
        UserName:登录用户名；参数类型为字符型
        Password：用户登录密码；参数类型为字符型
        FacilityId：设备所在车间号；参数类型为字符型
        方法返回值：
        方法的返回值是json格式的字符串。
        登录成功，返回格式如：
        {"success":true,"msg":{"userId":"ADMIN","userRrn":"20","facilityId":"HFM01","facilityRrn":"4961384"}}
        登录失败，返回格式如:
        {"success":false,"msg":"登录失败信息"}
        '''
        if not self.enabled:
            return True, 'MES未启动。'

        if self.client is None:
            return False, 'MES未连接成功。'
        try:
            response = self.client.service.login(user_name, password, facility_id)
            result = json.loads(response._value_1)
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=False))
            if result['success']:
                self.user_name = user_name
                return True, ''
            return False, result['msg']
        except requests.exceptions.RequestException:
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=True))
            return False, 'MES 连接出错'

    def dispatch_lot(self, el_data, vi_result=None):
        '''EL过站接口
        stand_alone：为True时表示独立和mes对接，而不是和原有硬件厂商的客户端同时和mes对接
        EL测试机台MES处理方法dispatchLotForEL方法：public String dispatchLotForEL(String facilityId, String userId, String eqipId, String lotIds, String transData)
        方法参数：
        facilityId：XTM01
        userId：xt0075
        eqipId：1EL101
        lotIds：["163M6K6051003243"]
        transData：{"parameter":{"collectionType":"BY_LOT","items":[]}}
        只需要替换其中的组件号
        '''
        if not self.user_name:
            return False, 'MES未登录'

        module_id = el_data.module_info.id
        file_path = el_data.img_info.ext_info["file_path"]
        logging.info('mes过账前: 组件号=%s, 图片地址=%s, 检测结果=%s', module_id, file_path, vi_result)
        # 图片路径映射
        mes_path_map = self.get_config('mes_path_map', False)
        if mes_path_map:
            new_file_path = image_transfer_for_mes(el_data, vi_result)
            if new_file_path:
                if os.path.exists(new_file_path):
                    file_path = new_file_path
                else:
                    logging.error('图片路径映射后地址不存在 %s', new_file_path)
            logging.info('完成图片路径映射到 %s', file_path)
        trans_data = {"parameter": {"collectionType": "BY_LOT", "items": []}}
        trans_data_items = self._generate_trans_data_items_stand_alone(module_id, vi_result)
        trans_data["parameter"]["items"] = trans_data_items["items"]

        try:
            logging.info('dispatch_lot_for_el:{}'.format(trans_data["parameter"]["items"]))
            logging.info('transData: %s' % trans_data)
            logging.info('开始mes过账: 车间=%s, 设备=%s, 组件=%s, 数据=%s',
                         self.facility_id, self.equip_id, module_id, trans_data)
            response = self.client.service.dispatchLot(self.facility_id, self.user_name, self.equip_id,
                                                       json.dumps([module_id]), json.dumps(trans_data))
            result = json.loads(response._value_1)
            logging.info('完成mes过账: 返回结果= %s', result)
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=False))
            return result['success'], result['msg']
        except requests.exceptions.RequestException:
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=True))
            return False, 'MES 连接出错'
        except Exception as e:
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesUploadError, is_err=True))
            logging.exception("mes过账失败: %s", e)

    def _generate_trans_data_items_stand_alone(self, module_id, defects):
        trans_data = {'items': []}
        reduce_rank = self.get_config('send_reduce_rank_message_in_cenghou', False)

        for (detail, locations) in defects.items():
            if not detail:
                logging.warning("缺陷code为空，不发送该条")
                continue
            if not locations:
                logging.warning("缺陷locations为空，不发送该条")
                continue

            for loc in locations:
                item = {
                    'location': loc,
                    'lotId': module_id,
                    'parameterSeq': '0',
                    'parameterId': 'FLD_GRADE',
                    'parameterValue': 'NG',
                    # 'reasonCode': 'RC1' if reduce_rank else defect_code['reasonCode'],
                    'reasonCode': '',
                    'reasonDetail': 'EL图片异常' if reduce_rank else detail
                }
                trans_data['items'].append(item)

        return trans_data

    @staticmethod
    def _lable_name2text(name):
        for xx in config.get_config('hp_defects', []):
            if xx['name'] == name:
                return xx['text']
        return None

    def get_el_horad(self, el_data, vi_result):
        """ 参数名GetELHorad
        LotId：串条码
        EquipId：串焊机的机台编号，比如：M19L3CJ-01 七线一号机 M19L3CJ-02 七线二号机 M19L4CJ-01 八线一号机，M19L4CJ-02 八线二号机，M19L4CJ-03 八线三号机
        TestType：测试类型，EL;VI 外观
        FaceType：A，B侧
        TestResult：检测结果：OK和NG
        BadType：缺陷类型
        Location：位置，1 第一片，2 第二片
        RequestTime：请求时间
        ManualResult：2,1,0（2手工判定OK ,1手工判定NG，0：AI判定）

        发送的JSON数据格式：
        {"data":[{"LotId":"20200422171150","EquipId":"M17L3CJ-01","TestType":"EL","FaceType":"B","TestResult":"OK","ManualResult":"","BadType":"","Location":"","RequestTime":"2021/7/1 17:12:15"}]}
        {"data":[{"LotId":"120200422171150","EquipId":"M17L3CJ-01","TestType":"EL","FaceType":"B","TestResult":"NG","BadType":"虚焊","Location":"3","RequestTime":"2021/7/1 17:12:15"},{"LotId":"120200422171150","EquipId":"M18L7CJ-01","FaceType":"B","TestResult":"NG","ManualResult":"1","BadType":"隐裂","Location":"6","RequestTime":"2021/7/1 17:12:15"}]}

        vi_result: [['隐裂','3'],['虚焊','6']]
        """
        module_id = el_data.module_info.id
        equip_id = el_data.mes_info.equip_id
        face_type = 'A' if "A" in module_id else 'B'
        request_time = time.strftime("%Y/%m/%d %H:%M:%S")
        is_ai_confirm = el_data.module_info.ext_info.get('is_ai_confirm', 'True')
        if is_ai_confirm:
            manaul_result = '0'
        else:
            manaul_result = '1' if vi_result else '2'
        # 构造数据
        data = {"data": []}

        if vi_result:
            # NG 组件
            for defect in vi_result:
                item = {
                    "LotId": module_id,
                    "EquipId": equip_id,
                    "TestType": "WG",
                    "FaceType": face_type,
                    "TestResult": "NG",
                    "BadType": defect[0],
                    "Location": defect[1],
                    "RequestTime": request_time,
                    'ManualResult': manaul_result
                }
                data['data'].append(item)
        else:
            # OK 组件
            item = {
                "LotId": module_id,
                "EquipId": equip_id,
                "TestType": "WG",
                "FaceType": face_type,
                "TestResult": "OK",
                "BadType": "",
                "Location": "",
                "RequestTime": request_time,
                'ManualResult': manaul_result
            }
            data['data'].append(item)

        try:
            logging.info('开始mes过账: 车间=%s, 设备=%s, 组件=%s, 数据=%s',
                         self.facility_id, self.equip_id, module_id, json.dumps(data, ensure_ascii=False))
            response = self.client.service.GetELHorad(json.dumps(data, ensure_ascii=False))

            logging.info("完成mes过账: 返回结果：%s, 返回值属性：%s", response, type(response))

            return response

        except requests.exceptions.RequestException:
            self.emit(HPEventType.ErrStatusChanged, ErrStatus(err_type=HPErrorType.MesConnectError, is_err=True))
            return 'MES 过账出错'

        except Exception as e:
            logging.exception("mes过账失败: %s", e)
            return 'MES 出错'

    @MesDataProcess.FLUSHCACHE
    def execute(self, vi_item):
        '''执行器'''
        vi_result = copy.deepcopy(vi_item.confirmed_result)
        vi_result.defects = copy.deepcopy(vi_item.vi_result.defects)
        station_stage = vi_item.el_data.module_info.station_stage

        if station_stage == 'cengqian':
            map_vi_defects = config.get_config("vi_defects_map", {})
            mes_defects = self.form_mes_defects(vi_result, map_vi_defects)
            logging.info("mes_defects:%s", mes_defects)
            succ, msg = self.dispatch_lot(vi_item.el_data, mes_defects)

        elif station_stage == 'chuanjian':
            mes_defects = []
            if vi_result.is_ng:
                defect_selected = vi_result.ext_info.get('defect_selected', None)
                if defect_selected:
                    # 人工复检ng   defect_selected:{"WG_Value4": ["F11", "F3"]}
                    for defect, loc_list in defect_selected.items():
                        for loc in loc_list:
                            mes_defects.append([self.defect_label_map.get(defect), loc.split("A")[-1]])
                elif vi_result.defects:
                    # AI 检测ng    vi_result.defects: [{'class': 'yinlie', 'prob': 0.99, 'loc': (1, 1), 'coord': (100, 120, 200, 220)},{'class': 'xuhan', 'prob': 0.99, 'loc': (1, 2), 'coord': (600, 100, 700, 200)}]
                    mes_defects = [[self._lable_name2text(i['class']), str(i['loc'][1])] for i in vi_result.defects]
                else:
                    mes_defects = [['无记录缺陷信息', '1']]
            logging.info("mes_defects:%s", mes_defects)
            # mes_defects: [['隐裂','3'],['虚焊','6']]
            msg = self.get_el_horad(vi_item.el_data, mes_defects)
        else:
            msg = "Mes出现问题, 暂不支持{}工序".format(station_stage)
            logging.error(msg)
        self.emit(HPEventType.StatusMessage, msg)

    def _plugin_def(self):
        '''返回插件定义
        实验插件须由插件代码返回插件定义对象，（标准插件则在plugin_def.yml中定义）
        '''
        plugin_def = '''
- name: MesAtsDaFengWG
  text: 阿特斯大丰外观mes
  description: 组装mes数据发送至mes
  tags:
    - 阿特斯大丰
  events:
    - OutputVIResult
  data: VIItem
  config:
      wsdl: 'http://10.222.40.40:8011/YcdfService.asmx?wsdl'
      mes_path_map: false
      send_reduce_rank_message_in_cenghou: false
  config_ui_def:
    wsdl:
      text: wsdl
      type: string
'''
        return yaml.load(plugin_def, Loader=yaml.FullLoader)[0]
