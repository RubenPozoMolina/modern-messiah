import yaml

class ConfigUtils:
    __config = None

    def __init__(self, config_path):
        self.config_path = config_path

    def load_config(self):
        try:
            self.__config = yaml.safe_load(open(self.config_path))

        except Exception as e:
            print(f"Error loading config: {e}")

    def get_config(self):
        return self.__config