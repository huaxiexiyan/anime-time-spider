import json

from spider import redis_client, app


class RedisUtils:
    @classmethod
    def get_keys(cls, pattern):
        keys = []
        cursor = 0
        while True:
            cursor, scanned_keys = redis_client.scan(cursor=cursor, match=pattern)
            keys.extend(scanned_keys)
            if cursor == 0:
                break
        return keys

    @classmethod
    def get_json_value(cls, key):
        try:
            # 从 Redis 获取数据
            data = redis_client.get(key)
            if data is None:
                return None  # 或者根据你的需求返回适当的值
            return json.loads(data)
        except json.JSONDecodeError as e:
            app.logger.exception('解析 JSON 时发生错误')
            return None

    @classmethod
    def set_json_str(cls, key, data):
        return redis_client.set(key, json.dumps(data))
