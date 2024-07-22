import json
import random
import time

import requests

from spider import redis_client, app
from spider.job.bilibil_api import BilibiliApi
from utils.redis_utils import RedisUtils


class BiliBiliTask:
    api_host = 'https://api.bilibili.com'
    cache_key_season_index = 'bilibili:season:index:'
    cache_key_season_details = 'bilibili:season:details:'
    cache_key_season_condition = 'bilibili:season:condition'

    def __init__(self):
        self.api_host = 'https://api.bilibili.com'

    def season_index_result_task(self):
        '''
        初始化番剧索引
        :return:
        '''
        app.logger.info('<<<<<<============ bilibili番剧索引查询任务【开始】 ============ >>>>>>')
        bilibili_api = BilibiliApi()
        page = 1
        while 1:
            try:
                response_json = bilibili_api.get_season_index_result('-1', page).json()
                if 'code' in response_json:
                    if response_json['code'] == 0:
                        # 设置存储键
                        redis_key = f'{self.cache_key_season_index}{page}'
                        r = RedisUtils.set_json_str(redis_key, response_json)
                        app.logger.info('请求正常完成，存储【%s】结果 【%s】', redis_key, r)
                        # 计算下一个请求参数
                        if response_json['data']['has_next'] == 1:
                            # 继续查询下一页
                            page += 1
                        else:
                            break
                        # 请求下一页前，暂停几秒
                        sleep_seconds = random.randint(3, 15)
                        app.logger.info('执行下个查询任务前准备休眠【%s】秒', sleep_seconds)
                        time.sleep(sleep_seconds)
                    else:
                        raise Exception('请求失败 code=【%s】', response_json['code'])
                else:
                    raise Exception('请求失败 code参数不存在，response_json=【%s】', response_json)
            except requests.exceptions.RequestException as e:
                # 捕获所有requests相关的异常，例如超时、连接错误等
                app.logger.exception('请求发生错误')
            except json.JSONDecodeError as e:
                # 捕获JSON解析错误 .exception  ，或者  .error(exc_info=True) 两者都可正常输出异常堆栈
                app.logger.error('解析响应JSON时发生错误', exc_info=True)
            except Exception as e:
                # 捕获其他异常,
                app.logger.exception('发生未预料的错误')
        app.logger.info('<<<<<<============ bilibili番剧索引查询任务【结束】 ============ >>>>>>')

    def season_index_condition_task(self):
        bilibili_api = BilibiliApi()
        response_json = bilibili_api.get_season_index_condition().json()
        if 'code' in response_json:
            if response_json['code'] == 0:
                r = RedisUtils.set_json_str(self.cache_key_season_condition, response_json)
            else:
                raise Exception('请求失败 code=【%s】', response_json['code'])
        else:
            raise Exception('请求失败 code参数不存在，response_json=【%s】', response_json)
        app.logger.info('请求正常完成 结果 【%s】', r)

    def season_details_task(self):
        '''
        初始化获取详情
        :return:
        '''
        # 1、获取列表
        # 2、查询详情
        # 3、存进redis
        app.logger.info('<<<<<<============ bilibili 番剧详情初始化任务【开始】 ============ >>>>>>')
        bilibili_api = BilibiliApi()
        keys = RedisUtils.get_keys(f'{self.cache_key_season_index}*')
        for key in keys:
            try:
                index_repose_json = RedisUtils.get_json_value(key)
                season_list_json = index_repose_json['data']['list']
                for season_index_json in season_list_json:
                    season_id = season_index_json['season_id']
                    app.logger.info('<<<<<<============ bilibili 番剧详情初始化任务【season_id=%s】 ============ >>>>>>',
                                    season_id)
                    season_details_response = bilibili_api.get_season_details(season_id).json()
                    if 'code' in season_details_response:
                        if season_details_response['code'] == 0:
                            # 设置存储键
                            redis_key = f'{self.cache_key_season_index}{season_id}'
                            r = redis_client.set(redis_key, json.dumps(season_details_response))
                            app.logger.info('请求正常完成，存储【%s】结果 【%s】', redis_key, r)
                            # 请求下一页前，暂停几秒
                            sleep_seconds = random.randint(3, 15)
                            app.logger.info('执行下个查询任务前准备休眠【%s】秒', sleep_seconds)
                            time.sleep(sleep_seconds)
                        else:
                            raise Exception('请求失败 code=【%s】', season_details_response['code'])
                    else:
                        raise Exception('请求失败 code参数不存在，response_json=【%s】', season_details_response)
            except requests.exceptions.RequestException as e:
                # 捕获所有requests相关的异常，例如超时、连接错误等
                app.logger.exception('请求发生错误')
            except json.JSONDecodeError as e:
                # 捕获JSON解析错误
                app.logger.exception('解析响应JSON时发生错误')
            except Exception as e:
                # 捕获其他异常,
                app.logger.exception('发生未预料的错误')
        app.logger.info('<<<<<<============ bilibili 番剧详情初始化任务【结束】 ============ >>>>>>')
