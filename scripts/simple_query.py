from src.lmstudio_utils import LMStudioUtils


def main():
    lm_studio_utils = LMStudioUtils(
        {
            "base_url": "http://localhost:1234/v1",
            "model": "deepseek-r1-distill-qwen-14b",
            "role": "user",
        }
    )

    response = lm_studio_utils.chat_completions(
        "¿Quiénes eran los doce apóstoles? ¿Puedes enumerarlos con el formato del fichero adjunto?",
        "input/personajes.yaml"
    )
    print(response)

if __name__ == "__main__":
    main()