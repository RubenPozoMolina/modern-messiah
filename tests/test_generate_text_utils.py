import pytest

from datetime import datetime

from mm.generate_text_utils import GenerateTextUtils

models = [
    "meta-llama/Llama-3.1-8B-Instruct"
]

class TestGenerateTextUtils:

    @pytest.mark.parametrize("model", models)
    def test_generate_text_utils(self, model):
        generate_text_utils = GenerateTextUtils(model)
        min_size = 2500
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open("tests/data/system.txt", "r") as file:
            system_content = file.read()
        with open("tests/data/user.txt", "r") as file:
            user_content = file.read()
        response = generate_text_utils.generate_text(
            system_content,
            user_content,
            f"target/{timestamp}_output.txt",
            min_size,
            "Spanish"
        )
        assert response["word_count"] > min_size

