import json
import random
import time

import requests

from spider import redis_client, app
from spider.job.bilibil_api import BilibiliApi


class BiliBiliTask:
    api_host = "https://api.bilibili.com"

    def __init__(self):
        self.api_host = "https://api.bilibili.com"

    @classmethod
    def season_index_task(cls):
        """
        查询番剧索引
        :return:
        """
        app.logger.info("<<<<<<============ bilibili番剧索引查询任务【开始】 ============ >>>>>>")
        bilibili_api = BilibiliApi()
        start_year = 2024
        end_year = 2025
        page = 1
        while 1:
            try:
                # 查询成功,存储redis中
                if start_year + 1 == end_year - 1:
                    redis_key = f"bilibili:{start_year}:{page}"
                else:
                    redis_key = f"bilibili:{start_year}_{end_year - 1}:{page}"
                is_exists = redis_client.exists(redis_key)
                if is_exists:
                    app.logger.info(
                        "请求参数 【start_year=%s】【end_year=%s】【page=%s】页, redis_key=【%s】 已经存储过了，将跳过该页",
                        start_year, end_year, page, redis_key)
                    continue
                response_json = bilibili_api.get_season_index(start_year, end_year, page).json()
                if start_year is None:
                    # 第一部动画：《Pauvre Pierrot》（《可怜的皮埃罗》），发行于1892年10月28日
                    start_year = 1892
                if "code" in response_json:
                    if response_json["code"] == 0:
                        if response_json["data"]["has_next"] == 1:
                            # 继续查询下一页
                            page += 1
                        else:
                            if start_year > 2015:
                                start_year -= 1
                                end_year -= 1
                            elif start_year == 2015:
                                start_year = 2010
                                end_year = 2015
                            elif 2000 < start_year < 2015:
                                start_year -= 5
                                end_year -= 5
                            elif start_year == 2000:
                                start_year = 1990
                                end_year = 2000
                            elif 1980 < start_year < 2000:
                                start_year -= 10
                                end_year -= 10
                            elif start_year == 1980:
                                start_year = None
                                end_year = 1980
                            else:
                                app.logger.info("准备退出")
                            page = 1
                    else:
                        if start_year + 1 == end_year:
                            redis_key = f"bilibili:fail:{start_year}:{page}"
                        else:
                            redis_key = f"bilibili:fail:{start_year}_{end_year - 1}:{page}"
                else:
                    if start_year + 1 == end_year:
                        redis_key = f"bilibili:fail:{start_year}:{page}"
                    else:
                        redis_key = f"bilibili:fail:{start_year}_{end_year - 1}:{page}"
                r = redis_client.set(redis_key, json.dumps(response_json))
                app.logger.info("请求正常完成，已存储结果 【%s】", r)
                if start_year is not None and start_year == 1892:
                    break
                else:
                    sleep_seconds = random.randint(3, 15)
                    app.logger.info("执行下个查询任务前准备休眠【%s】秒", sleep_seconds)
                    time.sleep(sleep_seconds)
            except requests.exceptions.RequestException as e:
                # 捕获所有requests相关的异常，例如超时、连接错误等
                app.logger.exception("请求发生错误")
            except json.JSONDecodeError as e:
                # 捕获JSON解析错误 .exception  ，或者  .error(exc_info=True) 两者都可正常输出异常堆栈
                app.logger.error("解析响应JSON时发生错误", exc_info=True)
            except Exception as e:
                # 捕获其他异常,
                app.logger.exception("发生未预料的错误")
        app.logger.info("<<<<<<============ bilibili番剧索引查询任务【结束】 ============ >>>>>>")
