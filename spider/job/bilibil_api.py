import requests
from spider import app


class BilibiliApi:

    @classmethod
    def get_season_index(cls, start_year, end_year, page) -> requests.Response:
        year = f"[{start_year},{end_year})"
        if page < 1:
            page = 1
        url = "https://api.bilibili.com/pgc/season/index/result"
        payload = {}
        params = {
            "st": 1,
            "order": 0,
            "season_version": -1,
            "spoken_language_type": -1,
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/126.0.0.0 Safari/537.36"}

        response = requests.get(url, json=payload, params=params, headers=headers, timeout=5)
        app.logger.info(
            f"请求参数 【start_year={start_year}】【end_year={end_year}】【page={page}】 页，实际请求: {response.request.url}")
        return response
