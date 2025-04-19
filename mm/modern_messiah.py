import os

from mm.book_utils import BookUtils
from mm.config_utils import ConfigUtils
from mm.generate_text_utils import GenerateTextUtils
from mm.generate_text_utils_claude import GenerateTextUtilsClaude


class ModernMessiah:
    languages = [
        {
            "name": "Spanish",
            "code": "es"
        },
        {
            "name": "English",
            "code": "en"
        },
        {
            "name": "French",
            "code": "fr"
        },
        {
            "name": "Chinese",
            "code": "zh"
        }
    ]

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
            dirs.sort()
            files.sort()
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append(full_path)
        return all_files

    def get_language_code(self, language_name):
        for language in self.languages:
            if language["name"] == language_name:
                return language["code"]
        return None

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
        chapter_file_name = f"{os.path.basename(chapter_path)}"
        output_chapter_path = "".join(
            [
                self.config["output_path"],
                os.sep,
                "chapters",
                os.sep,
                chapter_file_name
            ]
        )
        self.generate_text_utils.generate_text(
            self.common_info,
            chapter_content,
            output_chapter_path,
            self.config["chapter_min_size"],
            self.config["language"]
        )

    def write_book(self):
        if "output_path" in self.config:
            if not os.path.exists(self.config["output_path"]):
                os.makedirs(self.config["output_path"])
        self.get_common_info()
        chapters = self.get_all_files(
            self.config['data_path'] + os.sep + "chapters"
        )
        if "cover_generate" in self.config and self.config['cover_generate']:
            self.generate_text_utils.generate_svg(self.config)
        for chapter in chapters:
            file_name = os.path.basename(chapter)
            exclude_chapter = False
            if "excluded" in self.config and file_name in self.config[
                "excluded"]:
                exclude_chapter = True
            if not exclude_chapter:
                self.write_chapter(chapter)
        book_utils = BookUtils(
            self.config["output_path"],
            self.config["output_path"],
            self.config["title"],
            self.config["author"],
            self.config["cover"],
            self.get_language_code(self.config["language"]),
            self.config["book_type"]
        )
        book_utils.create_book()
