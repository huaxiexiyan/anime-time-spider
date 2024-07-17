# nacos配置
import threading
import time

import nacos
import yaml

from spider import app
from utils.inet_utils import InetUtils
from utils.yaml_utils import YamlUtils


class NacosService:
    nacos_config_client = None
    nacos_discovery_client = None
    nacos_yaml = None
    gunicorn_conf_path = None
    nacos_application_yaml = None

    def __init__(self, nacos_config_path, gunicorn_conf_path):
        self.gunicorn_conf_path = gunicorn_conf_path
        nacos_yaml = self.load_config(nacos_config_path)
        self.nacos_yaml = nacos_yaml
        nacos_yaml_config = nacos_yaml['nacos']['config']
        nacos_yaml_discovery = nacos_yaml['nacos']['discovery']

        # 创建连接客户端
        self.nacos_config_client = nacos.NacosClient(server_addresses=nacos_yaml_config['server-addr'],
                                                     namespace=nacos_yaml_config['namespace'],
                                                     username=nacos_yaml_config['username'],
                                                     password=nacos_yaml_config['password'])
        self.nacos_discovery_client = nacos.NacosClient(server_addresses=nacos_yaml_discovery['server-addr'],
                                                        namespace=nacos_yaml_discovery['namespace'],
                                                        username=nacos_yaml_discovery['username'],
                                                        password=nacos_yaml_discovery['password'])

    def pull_config(self):
        data_id = self.nacos_yaml['nacos']['import'][0]
        group = "DEFAULT_GROUP"
        nacos_config = self.nacos_config_client.get_config(data_id, group)
        self.nacos_application_yaml = YamlUtils.load_yaml_config_form_str(nacos_config)
        app.logger.info('[Nacos Config] Load config[dataId=%s, group=%s] success : \n%s', data_id, group, nacos_config)

    def register_instance(self):
        # 注册实例
        ipv4, ipv6 = InetUtils.find_first_non_loopback_address()
        metadata = {
            "preserved.register.source": "FLASK",
            'ipv6': f"[{ipv6}]"
        }
        # param service_name 必需要注册的服务名称。
        service_name = self.nacos_yaml['nacos']['application']['name']
        group_name = "DEFAULT_GROUP"
        # param port 必填实例的端口。
        port = self.get_port_from_bind()
        self.nacos_discovery_client.add_naming_instance(
            service_name=service_name,
            ip=ipv4,
            port=port,
            group_name=group_name,
            metadata=metadata
        )
        app.logger.info("nacos registry, %s %s %s:%s register finished", group_name, service_name, ipv4, port)
        # 注册完，定时发送心跳
        thread = threading.Thread(target=self.send_heartbeat, name="send_heartbeat_threads",
                                  args=(self.nacos_discovery_client, service_name, ipv4, port, group_name, metadata),
                                  daemon=True)
        thread.start()

    def send_heartbeat(self, client, service_name, ip, port, group_name, metadata):
        """
        发送心跳
        :param client: 服务注册 nacos 客户端
        :param service_name: 注册的服务名字
        :param ip: 注册服务的 ip
        :param port: 注册服务的 port
        :param group_name: 注册服务的分组
        :param metadata: 注册服务的其他参数
        :return:
        """
        while True:
            client.send_heartbeat(service_name, ip, port, group_name=group_name, metadata=metadata)
            # 每个 5 秒发送一次
            time.sleep(5)

    def get_port_from_bind(self):
        """
        优先获取 gunicorn.conf.py 配置的端口。否则返回 5000
        :return:
        """
        # 加载 gunicorn.conf.py
        try:
            config = self.load_gunicorn_config(self.gunicorn_conf_path)
            # 获取bind配置中的端口号
            bind = config.get('bind')
            port = bind.split(":")[-1]
        except Exception as e:
            # 捕获其他异常,
            app.logger.exception('加载 gunicorn.conf.py=【%s】 文件失败', self.gunicorn_conf_path)
            port = 5000
        return port

    def load_config(self, file_path):
        """
        加载 yaml 文件
        :param file_path:
        :return:
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        app.logger.info('成功加载 nacos 配置文件 %s : \n%s', file_path, config)
        return config

    def load_gunicorn_config(self, file_path):
        config = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            exec(f.read(), config)
        return config

# if __name__ == '__main__':
#     with open('nacos.yaml', 'r', encoding="utf-8") as file:
#         config = yaml.safe_load(file)
#     print(config)