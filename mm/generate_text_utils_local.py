import gc
import os
import time
import torch
from huggingface_hub import login

from mm.base_text_utils import BaseTextUtils


class GenerateTextUtilsLocal(BaseTextUtils):
    model = None
    pipeline = None
    config = None

    def __init__(
            self,
            model="meta-llama/Llama-3.1-8B-Instruct",
            config = None,
            logger = None
    ):
        super().__init__(logger)
        self.unload_model()
        login(token=os.getenv("HUGGINGFACE_TOKEN",""))
        self.model = model
        if not config:
            self.config = {
                "max_new_tokens": 2048,
                "do_sample": True,
                "temperature": 0.8,
                "top_p":0.9
            }
        else:
            self.config = config
        self.load_model()


    def generate_text(self, system_content, user_content):
        messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        messages.extend(self.conversation_history)
        self.logger.info("generate_text")
        for message in messages:
            self.logger.info(
                "%s", message
            )
        self.print_gpu_memory_stats()
        try:
            response = self.pipeline(
                messages,
                max_new_tokens=self.config["max_new_tokens"],
                do_sample=self.config["do_sample"],
                temperature=self.config["temperature"],
                top_p=self.config["top_p"]
            )
            return_value = ""
            for response_rol in response[0]["generated_text"]:
                if response_rol["role"] == "assistant":
                    return_value = response_rol["content"]
            if "Qwen" in self.model:
                return_value = self.clean_qwen_think_text(return_value)
            self.logger.info(
                "Generated text with %s words",
                self.count_words(return_value)
            )
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            self.wait_for_gpu_memory_release()
            self.load_model()
            return_value = self.generate_text(system_content, user_content)
        return return_value


    def unload_model(self):
        self.logger.info("Unloading model")
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None

        gc.collect()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.synchronize()

        self.print_gpu_memory_stats()

    def __del__(self):
        super().__del__()
        self.unload_model()

    def print_gpu_memory_stats(self):
        """Print current GPU memory usage."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1024 ** 2
            max_allocated = torch.cuda.max_memory_allocated() / 1024 ** 2
            reserved = torch.cuda.memory_reserved() / 1024 ** 2
            max_reserved = torch.cuda.max_memory_reserved() / 1024 ** 2

            self.logger.info(
                f"GPU Memory: Allocated: {allocated:.2f}MB (Max: {max_allocated:.2f}MB)")
            self.logger.info(
                f"GPU Memory: Reserved: {reserved:.2f}MB (Max: {max_reserved:.2f}MB)")

    def wait_for_gpu_memory_release(
            self,
            threshold_mb=500,
            check_interval=1.0,
            timeout=60
    ):
        if not torch.cuda.is_available():
            self.logger.info("CUDA no está disponible, no es necesario esperar")
            return True

        self.unload_model()

        start_time = time.time()
        attempt = 1

        while True:
            memory_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
            memory_reserved = torch.cuda.memory_reserved() / (1024 * 1024)

            self.logger.info(
                f"Try {attempt}: Memory GPU - assigned: {memory_allocated:.2f}MB, Reserved: {memory_reserved:.2f}MB")

            if memory_allocated < threshold_mb:
                elapsed = time.time() - start_time
                self.logger.info(
                    f"Memory GPU released below the threshold ({threshold_mb}MB) after {elapsed:.2f} seconds")
                return True

            if 0 < timeout < (time.time() - start_time):
                self.logger.warning(
                    f"Timeout reached after {timeout} seconds waiting for GPU memory release")
                return False

            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

            time.sleep(check_interval)
            attempt += 1

    @staticmethod
    def clean_qwen_think_text(text):
        return text.replace("<think>", "").replace("</think>", "")