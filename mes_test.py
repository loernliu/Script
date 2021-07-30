import os
import json

from zeep import Client
from zeep.transports import Transport
from zeep.cache import InMemoryCache


class MesTest(object):
    def __init__(self) -> None:
        super().__init__()
        self.connect()

    def connect(self):
        """连接"""
        cache = InMemoryCache(timeout=None)
        cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mes_cache', 'schemas.xmlsoap.org.xml')
        with open(cache_file, 'rb') as f:
            cache.add('http://schemas.xmlsoap.org/soap/encoding/', f.read())
        transport = Transport(cache=cache, timeout=3)
        print("MES 对象尝试连接")
        for ii in range(3):
            try:
                self.client = Client(wsdl=self.wsdl, transport=transport)
                break
            except Exception:
                print('MES 连接失败。')
                self.client = None
    
    def login(self, user_name, password, facility_id):
        if self.client is None:
            print('MES未连接成功')
            return False
        try:
            response = self.client.service.login(user_name, password, facility_id)
            # self.client./
            result = json.loads(response._value_1)
            if result['success']:
                self.user_name = user_name
                print("MES 登录成功")
                return True, ''
            return False, result['msg']
        except Exception:
            return False, 'MES 连接出错'

    def send_data(self):
        pass


if __name__ == "__main__":
    a = input("请输入测试mes的json数据格式:")
    input("mes是否需要登录(Y/N):")
    input("接口名称")
