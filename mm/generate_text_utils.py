import gc
import os
import torch
from huggingface_hub import login
from transformers import BitsAndBytesConfig, pipeline
from mm.image_utils import ImageUtils


class GenerateTextUtils:
    model = None
    pipeline = None


    def __init__(self, model="meta-llama/Llama-3.1-8B-Instruct"):
        login(token=os.getenv("HUGGINGFACE_TOKEN",""))
        self.model = model
        self.load_model()

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
            }
        )

    @staticmethod
    def count_words(text):
        return len(text.split())

    def extend_text(self, text, min_size):
        word_count = self.count_words(text)
        additional_words_needed = min_size - word_count

        system_content = "".join(
            [
                "Continue the story where you left off",
                "Add more details, scenes, and development to expand the story."
            ]
        )
        user_content = "".join(
            [
                f"The current story has {word_count} words, but I need at least {min_size} words.",
                f"Please continue the story where it left off by adding approximately {additional_words_needed} more words.",
                f"Here is the current text for you to continue:\n\n{text}"
            ]
        )

        continuation_messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        continuation = self.pipeline(
            continuation_messages,
            max_new_tokens=2048,
            do_sample=True,
            temperature=0.8,
            top_p=0.9
        )

        additional_content = ""
        for response_rol in continuation[0]["generated_text"]:
            if response_rol["role"] == "assistant":
                additional_content = response_rol["content"]
        content = text + "\n\n" + additional_content
        return content

    def generate_text(
            self,
            system_content,
            user_content,
            output_path,
            min_size,
            language
    ):
        system_prefix = "Is mandatory the answer contains almost " + str(
            min_size) + " words in " + language + "."
        messages = [
            {
                "role": "system",
                "content": system_prefix + system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        response = self.pipeline(
            messages,
            max_new_tokens=2048,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
        )
        content = ""
        for response_rol in response[0]["generated_text"]:
            if response_rol["role"] == "assistant":
                content = response_rol["content"]

        word_count = self.count_words(content)
        while word_count < min_size:
            content = self.extend_text(content, min_size)
            word_count = self.count_words(content)

        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(output_path, 'w') as f:
            f.write(content)

        return {
            "word_count": word_count,
            "output_path": output_path
        }

    def generate_svg(self, config):
        prompt = "".join(
            [
                "Generate an SVG image for a book cover.",
                "The size of the image must be 1200 height",
                "The size of the image must be 800 width",
                "The title should be: ", config["title"],
                "The author should be: ", config["author"],
                "The image must represent ", config["cover_description"],
                "The image must show the model ", config["model"],
                "I need output in SVG format.",
                "svg must not contain links",
                "svg must not contain images",
                "svg must not contain svg tags"
            ]
        )

        outputs = self.pipeline(
            prompt,
            max_new_tokens=4096,
            do_sample=True,
            temperature=0.8,
            top_p=0.9
        )

        content = outputs[0]["generated_text"]
        file_path = config["output_path"] + os.sep + "cover.svg"
        svg_start = content.find("<svg")
        svg_end = content.find("</svg>") + 6
        if svg_start == -1 or svg_end == -1:
            raise ValueError("No SVG content found response")

        svg_content = content[svg_start:svg_end].replace(
            "\n", ""
        ).replace("\t", "")

        with open(file_path, "wb") as f:
            f.write(svg_content.encode("utf-8"))

        ImageUtils.svg_to_jpg(file_path, config["cover"])


    def unload_model(self):
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()



    def __del__(self):
        self.unload_model()
