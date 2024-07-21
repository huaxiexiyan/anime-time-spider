import gevent.monkey

gevent.monkey.patch_all()

loglevel = 'info'
bind = "0.0.0.0:26001"
# 配置了日志就需要目录存在，否则会启动失败
# pidfile = "log/gunicorn.pid"
# accesslog = "log/access.log"
# errorlog = "log/debug.log"
# True 就是后台启动
# daemon = True

# 启动的进程数, 其实就是实例数（类似于一个服务部署了多个），之间的内存资源都不互通，启动多个需要考虑并发问题
# workers = multiprocessing.cpu_count()
workers = 1
# 同步网络模型
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
# 预加载应用: 在工作进程启动前预加载应用代码
preload_app = True
