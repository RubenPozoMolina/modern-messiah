import base64

import requests


class LMStudioUtils:
    config = None

    def __init__(self, config):
        self.config = config

    def get_models(self):
        return_value = None
        try:
            url = self.config['base_url'] + "/models"
            response = requests.get(
                url
            )
            if response.status_code == 200:
                response_json = response.json()
                return_value = response_json['data']
            else:
                print(f"Error getting models: {response.status_code}")
        except Exception as e:
            print(f"Error getting models: {e}")
        return return_value

    @staticmethod
    def get_file(file_path):
        return_value = None
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
            # file_base64 = base64.b64encode(file_content).decode("utf-8")
            return_value = {
                "type": "file",
                "file_data": {
                    "media_type": "text/yaml",
                    "data": file_content
                }
            }
        except Exception as e:
            print(f"Error getting file: {e}")
        return return_value

    def chat_completions(self, prompt, files=None):
        return_value = None
        try:
            url = self.config['base_url'] + "/chat/completions"
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "temperature": 0.7,
            }
            if isinstance(files, list):
                for file in files:
                    payload['messages'][0]['content'].append(
                        self.get_file(file)
                    )
            response = requests.post(
                url,
                json=payload
            )
            if response.status_code == 200:
                response_json = response.json()
                return_value = response_json['choices'][0]['message']['content']
            else:
                print(f"Error completing: {response.status_code} {response.text}")
        except Exception as e:
            print(f"Error completing: {e}")
        return return_value

    def completions(self, prompt, temperature=0.7, max_tokens=500):
        return_value = None
        try:
            url = self.config['base_url'] + "/completions"
            response = requests.post(
                url,
                json={
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            if response.status_code == 200:
                response_json = response.json()
                return_value = response_json['choices'][0]['text']
        except Exception as e:
            print(f"Error completing: {e}")
        return return_value
