import os
import anthropic

from mm.image_utils import ImageUtils


class GenerateTextUtilsClaude:
    client = None
    model_type = "claude"

    def __init__(self, model="claude-3-5-sonnet-20240620"):
        self.model = model
        self.load_model()

    def load_model(self):
        try:
            api_key = os.environ["ANTHROPIC_API_KEY"]
            self.client = anthropic.Anthropic(api_key=api_key)
        except KeyError:
            raise ValueError(
                "ANTHROPIC_API_KEY is missing"
            )
        except Exception as e:
            raise Exception(
                f"Error initializing Claude: {str(e)}"
            )

    @staticmethod
    def count_words(text):
        return len(text.split())

    def extend_text(self, text, min_size):
        word_count = self.count_words(text)
        additional_words_needed = min_size - word_count

        system_content = (
            "Continue the story where you left off. "
            "Add more details, scenes, and development to expand the story."
        )

        user_content = (
            f"The current story has {word_count} words, but I need at least {min_size} words. "
            f"Please continue the story where it left off by adding approximately {additional_words_needed} more words. "
            f"Here is the current text for you to continue:\n\n{text}"
        )

        message = self.client.messages.create(
            model=self.model,
            system=system_content,
            messages=[
                {"role": "user", "content": user_content}
            ],
            max_tokens=4000,
            temperature=0.8,
            top_p=0.9
        )

        additional_content = message.content[0].text
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
        system_prefix = f"Is mandatory the answer contains almost {min_size} words in {language}. "

        message = self.client.messages.create(
            model=self.model,
            system=system_prefix + system_content,
            messages=[
                {"role": "user", "content": user_content}
            ],
            max_tokens=4000,
            temperature=0.8,
            top_p=0.9
        )

        content = message.content[0].text

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
        message = self.client.messages.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.8,
            top_p=0.9
        )
        file_path = config["output_path"] + os.sep + "cover.svg"
        svg_content = message.content[0].text
        svg_start = svg_content.find("<svg")
        svg_end = svg_content.find("</svg>") + 6
        if svg_start == -1 or svg_end == -1:
            raise ValueError("No SVG content found in Claude's response")

        svg_content = svg_content[svg_start:svg_end]

        with open(file_path, "wb") as f:
            f.write(svg_content.encode("utf-8"))

        ImageUtils.svg_to_jpg(file_path, config["cover"])