import os
import anthropic

from mm.base_text_utils import BaseTextUtils


class GenerateTextUtilsClaude(BaseTextUtils):
    client = None
    model_type = "claude"

    def __init__(self, model="claude-3-5-sonnet-20240620", logger=None):
        super().__init__(logger)
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

    def generate_text(self, system_content, user_content):
        messages = []
        messages.extend(self.conversation_history)
        return_value = ""
        try:
            message = self.client.messages.create(
                model=self.model,
                system=system_content,
                messages=messages,
                max_tokens=6000,
                temperature=0.8,
                top_p=0.9
            )
            return_value = message.content[0].text
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
        return return_value

    def unload_model(self):
        del self.client
        self.client = None

    def __del__(self):
        super().__del__()
        self.unload_model()