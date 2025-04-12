import os
import anthropic


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