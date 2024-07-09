import threading

from spider.job.bilibil_tsak import BiliBiliTask
from spider import redis_client, app

def start_job():
    """
    启动定时任务
    :return:
    """
    bilibili_task = BiliBiliTask()
    thread = threading.Thread(target=bilibili_task.season_index_task)
    thread.start()
