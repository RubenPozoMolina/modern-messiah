import os
import pytest
from datetime import datetime

from mm.generate_text_utils_local import GenerateTextUtilsLocal

MIN_SIZE = 500
MAX_SIZE = 1000

models = [
    {
        "name": "mistralai/Mistral-7B-Instruct-v0.3",
        "config": {
            "max_new_tokens": 4096,
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.9
        }
    },
    {
        "name": "meta-llama/Llama-3.1-8B-Instruct",
        "config": {
            "max_new_tokens": 2048,
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.9
        }
    },
    {
        "name": "Qwen/Qwen3-1.7B",
        "config": {
            "max_new_tokens": 2048,
            "do_sample": True,
            "temperature": 0.8,
            "top_p": 0.9
        }
    }
]


class TestGenerateTextUtils:

    @pytest.mark.parametrize("model", models)
    def test_generate_text_utils_local(self, model):
        generate_text_utils = GenerateTextUtilsLocal(
            model["name"],
            model["config"]
        )
        min_size = MIN_SIZE
        max_size = MAX_SIZE
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open("tests/data/system.txt", "r") as file:
            system_content = file.read()
        with open("tests/data/user.txt", "r") as file:
            user_content = file.read()
        model_file = model["name"].replace("/", "_")
        response = generate_text_utils.generate_text_to_file(
            system_content,
            user_content,
            f"target/{timestamp}_{model_file}_output.txt",
            min_size,
            max_size,
            "Spanish"
        )
        assert response["word_count"] > min_size
        del generate_text_utils

    @pytest.mark.parametrize("model", models)
    def test_generate_svg(self, model):
        cover = f"target/local_test/{model["name"].replace('/', '_')}.jpg"
        config = {
            "title": "test title",
            "author": "test author",
            "cover_description": "a red ball",
            "cover": cover,
            "model": model["name"],
            "output_path": "target/local_test"
        }
        if not os.path.exists(config["output_path"]):
            os.makedirs(config["output_path"])
        generate_text_utils = GenerateTextUtilsLocal(
            model["name"],
            model["config"]
        )
        generate_text_utils.generate_svg(config)
        del generate_text_utils
