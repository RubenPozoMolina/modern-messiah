import gc
import os
import torch
from huggingface_hub import login
from transformers import BitsAndBytesConfig, pipeline
from mm.base_text_utils import BaseTextUtils


class LlamaChatbot(BaseTextUtils):
    model = None
    pipeline = None
    conversation_history = []

    def __init__(
            self,
            model="meta-llama/Llama-3.1-8B-Instruct",
            system_message="",
            logger=None
    ):
        super().__init__(logger)
        login(token=os.getenv("HUGGINGFACE_TOKEN", ""))
        self.model = model
        self.load_model()

        self.system_message = system_message
        self.conversation_history = [
            {"role": "system", "content": self.system_message}
        ]

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

    def chat(self, user_input):
        self.conversation_history.append(
            {"role": "user", "content": user_input})
        self.logger.info(f"Conversation history:: {len(self.conversation_history)}")
        response = self.pipeline(
            self.conversation_history,
            max_new_tokens=4096,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        assistant_response = ""
        try:
            for response_rol in response[0]["generated_text"]:
                if response_rol["role"] == "assistant":
                    assistant_response = response_rol["content"]
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error extracting response: {str(e)}")
            else:
                print(f"Error extracting response: {str(e)}")

        if assistant_response:
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_response})

        return assistant_response

    def get_conversation_history(self):
        return self.conversation_history[1:]

    def reset_conversation(self):
        self.conversation_history = [
            {"role": "system", "content": self.system_message}
        ]

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
