import os
import tempfile

import yaml

from spider import app


class YamlUtils:

    @classmethod
    def load_yaml_config_form_str(cls, str) -> dict:
        config = yaml.safe_load(str)
        return config

    @classmethod
    def load_yaml_config(cls, file_path) -> dict:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config

    @classmethod
    def save_yaml_config(cls, config, file_path):
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.safe_dump(config, file)

    @classmethod
    def save_yaml_config_temp(cls, config):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml')
        with open(temp_file.name, 'w', encoding='utf-8') as file:
            yaml.safe_dump(config, file)
        return temp_file

    @classmethod
    def delete_file(cls, filename):
        if os.path.exists(filename):
            os.remove(filename)
            app.logger.info('成功删除文件: %s', filename)
