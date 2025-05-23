import os
import logging
from datetime import datetime

import torch
from transformers import BitsAndBytesConfig, pipeline

from mm.image_utils import ImageUtils

DEFAULT_SVG = """
<svg width="800" height="1200" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="white"/>
</svg>    
"""

class BaseTextUtils:

    logger = None
    conversation_history = []
    model = None
    pipeline = None
    cover_file = None
    system_content = ""
    user_content = ""
    config = None

    def __init__(self, logger = None):
        # os.environ["PYTORCH_CUDA_ALLOC_CONF"]="expandable_segments:True"
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.logger.addHandler(logging.StreamHandler())

    def load_model(self):
        # Configure 4-bit quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        self.pipeline = pipeline(
            "text-generation",
            model=self.model,
            model_kwargs={
                "torch_dtype": torch.float16,
                "device_map": "auto",
                "quantization_config": quantization_config
            },
            trust_remote_code = True
        )

    @staticmethod
    def count_words(text):
        return len(text.split())

    def generate_text(self, system_content, user_content):
        raise NotImplementedError

    def generate_text_to_file(
            self,
            system_content,
            user_content,
            output_path,
            min_size,
            max_size,
            language
    ):
        self.logger.info("Begin generate_text_to_file")
        system_prefix = f"Is mandatory the answer contains between {min_size} and {max_size} words in " + language + "."
        if "Qwen" in self.model:
            system_prefix += " Do not include any thinking process, internal reasoning or notes to yourself in your response. Provide only the final output without any <thinking> tags or similar markers."
        self.system_content = system_prefix + system_content
        self.conversation_history.append(
            {"role": "user", "content": user_content}
        )
        content = self.generate_text(self.system_content, user_content)
        self.conversation_history.append(
            {"role": "assistant", "content": content}
        )
        word_count = self.count_words(content)
        while word_count < min_size or word_count > max_size:
            content = self.extend_text(content, min_size, max_size)
            word_count = self.count_words(content)
            self.logger.info(
                f"{output_path} word count: {word_count}"
            )

        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_path, 'w') as f:
            f.write(content)

        self.logger.info(
            "End generate_text_to_file %s %s",
            output_path,
            word_count
        )
        return {
            "word_count": word_count,
            "output_path": output_path
        }

    def extend_text(self, text, min_size, max_size):
        word_count = self.count_words(text)

        system_content = "".join(
            [
            self.system_content,
            "Important: Do not apologize when correcting errors or providing information. Never use phrases like 'I'm sorry', 'I apologize', 'pardon me', or similar expressions. Provide information directly, accurately, and confidently without any form of apology.",
            f"The text must have between {min_size} and {max_size} words.",
            "Add more details to scenes and development to expand the story.",
            "Avoid duplications.",
            "Avoid unfinished sentences.",
            "Avoid clarifications or explanations about generated text."
            ]
        )

        user_content = (
            f"The current story has {word_count} words, but I need between {min_size} and {max_size} words. "
        )

        self.conversation_history.append(
            {"role": "user", "content": user_content}
        )
        generated_text = self.generate_text(system_content, user_content)
        self.conversation_history.append(
            {"role": "assistant", "content": generated_text}
        )
        return generated_text


    def generate_svg(self, config):
        prompt = "".join(
            [
                "Generate an SVG image for a book cover. ",
                "The size of the image must be 1200 height. ",
                "The size of the image must be 800 width. ",
                "The title should be: ", config["title"], ". "
                "The author should be: ", config["author"], ". ",
                "The image must represent ", config["cover_description"], ". ",
                "The image must show the model ", config["model"], ". ",
                "I need output in SVG format. ",
                "Generated svg must not contain links. ",
                "Generated svg must not contain images. ",
                "Generated svg must not contain svg tags. "
            ]
        )

        self.conversation_history.append(
            {"role": "user", "content": prompt}
        )
        content = self.generate_text("", prompt)
        self.cover_file = "".join(
            [
                config["output_path"],
                os.sep,
                datetime.now().strftime("%Y%m%d%H%M%S"),
                "_cover.svg"
            ]
        )
        try:
            svg_start = content.find("<svg")
            svg_end = content.find("</svg>") + 6
            svg_content = content[svg_start:svg_end].replace(
                "\n", ""
            ).replace("\t", "")

            with open(self.cover_file, "wb") as f:
                f.write(svg_content.encode("utf-8"))
            ImageUtils.svg_to_jpg(self.cover_file , config["cover"])
        except Exception as e:
            self.logger.error(
                "Error converting SVG to JPG: %s %s",
                str(e),
                content
            )
            with open(self.cover_file, "wb") as f:
                svg_content = DEFAULT_SVG
                f.write(svg_content.encode("utf-8"))
            ImageUtils.svg_to_jpg(self.cover_file, config["cover"])

    def __del__(self):
        self.cleanup_logger()

    def cleanup_logger(self):
        if self.logger:
            if hasattr(self.logger, 'handlers'):
                for handler in self.logger.handlers[:]:
                    handler.close()
                    self.logger.removeHandler(handler)
            self.logger = None
