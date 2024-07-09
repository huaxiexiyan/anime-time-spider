# 应用模块，包含所有与应用逻辑相关的内容。
import os
import logging
from flask import Flask
from logging.config import dictConfig
from flask_redis import FlaskRedis

# 日志配置
dictConfig({
    'version': 1,
    'formatters': {
        'default': { # %()s 文字靠右，左边补空格。 # %()-s 文字靠左，右边补空格
            'format': '%(asctime)s %(levelname)-7s %(name)-10s [%(lineno)4d] %(module)-15s : %(message)s'
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': './anime-time-spider.log',  # 设置日志文件路径
            'formatter': 'default',
            'encoding': 'utf8'
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

# 配置Redis连接
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')

# 初始化Flask-Redis
redis_client = FlaskRedis(app, decode_responses=True)


def initialize_redis():
    try:
        redis_client.ping()
        app.logger.info('Redis已经成功')
    except Exception as e:
        app.logger.error('Redis连接失败: %s',e)


# 注册路由
from spider.api import aliyun_drive_task_api

app.register_blueprint(aliyun_drive_task_api.bp, url_prefix="/api/aliyun-drives")

# 启动简单循环job
from spider.job.launcher import start_job

start_job()
