import re

from spider import app
from utils.yaml_utils import YamlUtils


class EnvParameterUtils:

    @classmethod
    def replace_placeholders(cls, config, replacements):
        # 使用递归方法来替换配置中的占位符
        if isinstance(config, dict):
            return {k: cls.replace_placeholders(v, replacements) for k, v in config.items()}
        elif isinstance(config, list):
            return [cls.replace_placeholders(i, replacements) for i in config]
        elif isinstance(config, str):
            pattern = re.compile(r'\$\{([^}]+)\}')
            matches = pattern.findall(config)
            for match in matches:
                config = config.replace(f"${{{match}}}", replacements.get(match, f"${{{match}}}"))
            return config
        else:
            return config

    @classmethod
    def load_and_replace_config(cls, yaml_path, replacements):
        config = YamlUtils.load_yaml_config(yaml_path)
        app.logger.info('成功加载nacos模版配置文件: \n %s', config)
        return cls.replace_placeholders(config, replacements)
