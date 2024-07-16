import threading

from spider.job.bilibil_tsak import BiliBiliTask

def start_job():
    """
    启动定时任务
    :return:
    """
    bilibili_task = BiliBiliTask()
    # thread = threading.Thread(target=bilibili_task.season_index_result_task)
    # thread = threading.Thread(target=bilibili_task.season_index_condition_task)
    # thread.start()
