import json
import threading
import requests
from spider import redis_client, app


def task_demo():
    url = "https://api.bilibil.com/pgc/season/index/result"
    url = "http://127.0.0.1:26000/api/anime2"
    payload = {}
    year = 2025
    page = 1
    params = {
        'st': '1',
        'order': '0',
        'season_version': '-1',
        'spoken_language_type': '-1',
        'is_finish': '-1',
        'copyright': '-1',
        'season_status': '-1',
        'season_month': '-1',
        'year': f'[{year - 1},{year})',  # 查询年费，这个是 2024年的
        'style_id': '-1',
        'sort': '0',  # 0是倒序，1顺序
        'page': '1',  # 页码，从 1 开始
        'season_type': '1',
        'pagesize': '20',  # 页码数量
        'type': '1',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    try:
        print('我执行了')
        response = requests.get(url, json=payload, params=params, headers={}, timeout=5)
        app.logger.info(f'请求 {year} 年 第 {page} 页，实际请求: {response.request.url}')
        # result_json.data.has_next = 1 有下一页， 0 表示没有
        response_json = response.json()
        app.logger.info(response_json)
        if 'code' in response_json:
            if response_json['code'] == 0:
                # 查询成功,存储redis中
                redis_client.set(f'blibli:{year}:{page}', json.dumps(response_json))
                app.logger.info('响应正常，储存正常')
            else:
                redis_client.set(f'blibli:fail:{year}:{page}', json.dumps(response_json))
                app.logger.info('响应异常')
        else:
            redis_client.set(f'blibli:fail:{year}:{page}', json.dumps(response_json))
            app.logger.info('响应异常,缺失参数code')
    except requests.exceptions.RequestException as e:
        # 捕获所有requests相关的异常，例如超时、连接错误等
        app.logger.info(f'请求 {year} 年 第 {page} 页时发生错误: {e}')
    except json.JSONDecodeError as e:
        # 捕获JSON解析错误
        app.logger.info(f'解析响应JSON时发生错误: {e}')
    except Exception as e:
        # 捕获其他异常
        app.logger.info(f'发生未预料的错误: {e}')


def start_job():
    """
    启动定时任务
    :return:
    """
    thread = threading.Thread(target=task_demo)
    thread.start()
