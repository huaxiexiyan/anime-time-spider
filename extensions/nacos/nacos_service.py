# nacos配置

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
        if nacos_yaml_config['server-addr'] == nacos_yaml_discovery['server-addr']:
            app.logger.info('<<<<<<============ 配置中心与注册中心地址一样，只需共用一个客户端 ============>>>>>')
            self.nacos_discovery_client = self.nacos_config_client
        else:
            app.logger.info('<<<<<<============ 注册中心与配置中心地址不一样，创建注册中心连接客户端 ============>>>>>')
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
        app.logger.info("获取实例ip地址, ipv4=【%s】; ipv6=【%s】", ipv4, ipv6)
        metadata = {
            "preserved.register.source": "FLASK"
        }
        if ipv6 is not None:
            metadata['ipv6'] = f"[{ipv6}]"
        # param service_name 必需要注册的服务名称。
        service_name = self.nacos_yaml['nacos']['application']['name']
        group_name = "DEFAULT_GROUP"
        # param port 必填实例的端口。
        port = self.get_port_from_bind()
        # heartbeat_interval=5 设置该参数即可启动心跳维护
        self.nacos_discovery_client.add_naming_instance(
            service_name=service_name,
            ip=ipv4,
            port=port,
            group_name=group_name,
            metadata=metadata,
            heartbeat_interval=5
        )
        app.logger.info("nacos 注册实例【%s %s %s:%s】成功", group_name, service_name, ipv4, port)

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
