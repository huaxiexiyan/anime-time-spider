import requests

from spider import app


class BilibiliApi:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/126.0.0.0 Safari/537.36"}
    access_key = '#'

    @classmethod
    def get_season_index_result(cls, year, page) -> requests.Response:
        """
        番剧索引
        :param year: 全部是 -1，范围 [start_year, end_year)
        :param page:
        :return:
        """
        if page < 1:
            page = 1
        url = "https://api.bilibili.com/pgc/season/index/result"
        payload = {}
        params = {
            "st": 1,
            "order": 5,
            "season_version": -1,
            "spoken_language_type": -1,
            "area": -1,
            "is_finish": -1,
            "copyright": -1,
            "season_status": -1,
            "season_month": -1,
            "year": year,  # 查询年费，这个是 2024年的
            "style_id": -1,
            "sort": 0,  # 0是倒序，1顺序
            "page": page,  # 页码，从 1 开始
            "season_type": 1,
            "pagesize": 20,  # 页码数量
            "type": 1,
        }
        response = requests.get(url, json=payload, params=params, headers=cls.headers, timeout=5)
        app.logger.debug("请求参数【year=%s】【page=%s】页，实际请求【%s】", year, page, response.request.url)
        return response

    @classmethod
    def get_season_index_condition(cls) -> requests.Response:
        url = "https://api.bilibili.com/pgc/season/index/condition"
        payload = {}
        params = {
            "access_key": cls.access_key,
            "actionKey": 'appkey',
            "appkey": '27eb53fc9058f8c3',
            "build": 80300100,
            "c_locale": 'zh-Hans_CN',
            "device": 'phone',
            "disable_rcmd": 0,
            "mobi_app": 'iphone',
            "platform": 'ios',
            "s_locale": 'zh-Hans_CN',
            "season_type": 1,  # 查询年费，这个是 2024年的
            "sign": 'a19fa36f74a23e61e1733480442abf9e',
            "statistics": '{"appId":1,"version":"8.3.0","abtest":"","platform":1}',  # 0是倒序，1顺序
            "ts": 1720843281,  # 页码，从 1 开始
            "type": 0,  # 页码，从 1 开始
        }
        response = requests.get(url, json=payload, params=params, headers=cls.headers, timeout=5)
        app.logger.debug("实际请求【%s】", response.request.url)
        app.logger.debug("请求响应%s", response.json())
        return response

    @classmethod
    def get_season_details(cls, season_id) -> requests.Response:
        """
        获取详情
        :param season_id:
        :return:
        """
        url = "https://api.bilibili.com/pgc/view/web/season"
        payload = {}
        params = {
            "season_id": season_id
        }
        response = requests.get(url, json=payload, params=params, headers=cls.headers, timeout=5)
        app.logger.debug("请求参数【season_id=%s】，实际请求【%s】", season_id, response.request.url)
        return response
