import os
from datetime import datetime

from mm.config_utils import ConfigUtils
from mm.generate_text_utils import GenerateTextUtils
from mm.generate_text_utils_claude import GenerateTextUtilsClaude


class ModernMessiah:

    config = None
    generate_text_utils = None
    common_info = None

    def __init__(self, config_path):
        config_utils = ConfigUtils(config_path)
        config_utils.load_config()
        self.config = config_utils.get_config()
        if self.config['type'] == "claude":
            self.generate_text_utils = GenerateTextUtilsClaude(
                self.config["model"]
            )
        else:
            self.generate_text_utils = GenerateTextUtils(self.config["model"])

    @staticmethod
    def get_all_files(directory_path):
        all_files = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append(full_path)
        return all_files

    @staticmethod
    def get_timestamp():
        return datetime.now().strftime("%Y%m%d%H%M%S")

    def get_common_info(self):
        self.common_info = ""
        common_files = self.get_all_files(
            self.config['data_path'] + os.sep + "common"
        )
        for file in common_files:
            with open(file, "r") as f:
                self.common_info += f.read() + "\n\n"

    def write_chapter(self, chapter_path):
        with open(chapter_path, "r") as f:
           chapter_content = f.read()
        timestamp = self.get_timestamp()
        chapter_file_name =  f"{timestamp}_{os.path.basename(chapter_path)}"
        self.generate_text_utils.generate_text(
            self.common_info,
            chapter_content,
            self.config["output_path"] + os.sep + chapter_file_name,
            self.config["chapter_min_size"],
            self.config["language"]
        )

    def write_book(self):
        self.get_common_info()
        chapters = self.get_all_files(
            self.config['data_path'] + os.sep + "chapters"
        )
        for chapter in chapters:
            self.write_chapter(chapter)
