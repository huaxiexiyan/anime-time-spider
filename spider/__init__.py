# 应用模块，包含所有与应用逻辑相关的内容。
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from logging.config import dictConfig

from flask import Flask
from flask_redis import FlaskRedis


# ======================== flask配置 ================================
# 日志配置
class HeartbeatFilter(logging.Filter):
    def filter(self, record):
        # 仅过滤 INFO 级别的 [send-heartbeat] 日志
        return not (record.levelno == logging.INFO and '[send-heartbeat]' in record.getMessage())


dictConfig({
    'version': 1,
    'formatters': {
        'default': {  # %()s 文字靠右，左边补空格。 # %()-s 文字靠左，右边补空格
            'format': '%(asctime)s %(levelname)-7s %(name)-12s [%(lineno)4d] %(module)-15s : %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default',
            'filters': ['heartbeat_filter']  # 应用过滤器
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './anime-time-spider.log',  # 设置日志文件路径
            'formatter': 'default',
            'encoding': 'utf8',
            'filters': ['heartbeat_filter']  # 应用过滤器
        }
    },
    'filters': {
        'heartbeat_filter': {
            '()': HeartbeatFilter
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi', 'file']  # 同时记录到控制台和文件
    }
})

# 创建和配置应用
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# 在未测试时加载实例配置（如果存在）
app.config.from_pyfile('config.py', silent=True)

# 确保实例文件夹存在
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

app.logger.info('<<<<<<======================== flask 初始化 start ================================>>>>>> ')
# ======================== 其他连接配置 ================================
from utils.env_parameter_utils import EnvParameterUtils, YamlUtils
import uuid
import atexit

# 读取环境变量
env_nacos_address = os.environ.get('nacos.server.address')
env_nacos_namespace = os.environ.get('nacos.namespace')
env_nacos_username = os.environ.get('nacos.username')
env_nacos_password = os.environ.get('nacos.password')
app.logger.info(
    '加载环境变量参数: \nacos.server.address=【%s】\nnacos.namespace=【%s】\nnacos.username=【%s】\nnacos.password=【%s】',
    env_nacos_address, env_nacos_namespace, env_nacos_username, env_nacos_password)

replacements = {
    'nacos.server.address': env_nacos_address,
    'nacos.namespace': env_nacos_namespace,
    'nacos.username': env_nacos_username,
    'nacos.password': env_nacos_password
}
project_path = os.path.dirname(app.root_path)
app.logger.info('获取项目根路径: %s', project_path)
config = EnvParameterUtils.load_and_replace_config(os.path.join(project_path, 'nacos.yaml'), replacements)
nacos_config_yaml_path = os.path.join(project_path, f'nacos-{uuid.uuid1().hex}.yaml')
YamlUtils.save_yaml_config(config, nacos_config_yaml_path)
# 注册事件，当应用结束前，删除临时文件
atexit.register(YamlUtils.delete_file, nacos_config_yaml_path)

# 注册 nacos
from extensions.nacos.nacos_service import NacosService

gunicorn_conf_path = os.path.join(os.path.dirname(app.root_path), 'gunicorn.conf.py')
nacos_service = NacosService(nacos_config_path=nacos_config_yaml_path, gunicorn_conf_path=gunicorn_conf_path)
nacos_service.pull_config()
nacos_service.register_instance()
bind_port = nacos_service.get_port_from_bind()
app.logger.info('<<<<<<======================== nacos 注册 end ================================>>>>>>')

# 配置Redis连接
nacos_redis_config_yaml = nacos_service.nacos_application_yaml['redis']
app.config['REDIS_URL'] = nacos_redis_config_yaml['url']
# 初始化Flask-Redis
redis_client = FlaskRedis(app, decode_responses=True)
try:
    redis_client.ping()
    app.logger.info('<<<<<<======================== Redis连接成功: %s ================================>>>>>>',
                    app.config['REDIS_URL'])
except Exception as e:
    app.logger.exception('<<<<<<======================== Redis连接失败: %s ================================>>>>>>')

# ======================== 应用启动后配置 ================================
# 启动简单循环job
# from spider.job.launcher import start_job
#
# start_job()
# 注册路由
from spider.api import bilibili_bp

app.register_blueprint(bilibili_bp.bp, url_prefix="/bilibili")


#
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = rule.rule
        line = "{:50s} {:20s} {}".format(url, methods, options)
        output.append(line)
    return "\n".join(output)


app.logger.info('已注册的路由地址如下: \n%s', list_routes())

# 初始化一个线程池
common_executor = ThreadPoolExecutor(max_workers=12, thread_name_prefix='common-thread-pool')  # 根据需要设置线程池的大小
atexit.register(lambda: common_executor.shutdown(wait=True))
app.logger.info('<<<<<<======================== flask 初始化 end ================================>>>>>> ')
