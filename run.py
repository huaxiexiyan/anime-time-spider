# 用于启动应用的脚本。
import spider
from spider import app

if __name__ == '__main__':
    app.run(debug=False, port=spider.bind_port)
