import os
import transformers
import torch
from huggingface_hub import login
from transformers import BitsAndBytesConfig


class GenerateTextUtils:
    model = None
    pipeline = None
    model_type = None

    def __init__(self, model="meta-llama/Llama-3.1-8B-Instruct"):
        login(token=os.environ["HUGGINGFACE_TOKEN"])
        self.model = model
        self.load_model()

    def load_model(self):
        quantization_config = BitsAndBytesConfig(
            device_map="auto",
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )

        self.pipeline = transformers.pipeline(
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

        # Crear mensajes según el tipo de modelo
        if self.model_type == "deepseek":
            # DeepSeek utiliza un formato específico
            continuation_messages = [
                {
                    "role": "user",
                    "content": f"{system_content}\n\n{user_content}"
                }
            ]
        else:
            # Para Llama y otros modelos
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

        additional_content = continuation[0]["generated_text"][-1]['content']
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

        outputs = self.pipeline(
            messages,
            max_new_tokens=4096,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1
        )

        response = outputs[0]["generated_text"][-1]
        content = response['content']

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
                "The title should be: ", config["title"],
                "The author should be: ", config["author"],
                "The image must represent ", config["cover_description"],
                "The image must show the model ", config["model"]
            ]
        )

        outputs = self.pipeline(
            prompt,
            max_new_tokens=4096,
            do_sample=True,
            temperature=0.8,
            top_p=0.9,
            repetition_penalty=1.1
        )

        response = outputs[0]["generated_text"][-1]
        content = response['content']
        file_path = config["cover"]
        with open(file_path, "wb") as f:
            f.write(content[0].image)