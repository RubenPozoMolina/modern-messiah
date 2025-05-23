import anthropic
import os


def run_claude_model(api_key: str = None,
                     system_prompt: str = "You are a pirate chatbot who always responds in pirate speak!",
                     user_message: str = "Who are you?",
                     model: str = "claude-3-7-sonnet-20250219",
                     max_tokens: int = 512,
                     temperature: float = 0.7):
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key is None:
            raise ValueError(
                "ANTHROPIC_API_KEY is mising"
            )

    client = anthropic.Anthropic(api_key=api_key)

    try:
        print(f"Sending requests to Claude ({model})...")

        response = client.messages.create(
            model=model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Extraer la respuesta
        assistant_response = response.content[0].text

        print("\nRespuesta de Claude:")
        print(assistant_response)

        return assistant_response

    except Exception as e:
        print(f"Error al llamar a la API de Claude: {e}")

        # Sugerencias para solucionar problemas comunes
        print("\nPosibles soluciones:")
        print("1. Verifica que tu clave API sea válida")
        print(
            "2. Asegúrate de tener instalada la última versión de la biblioteca anthropic:")
        print("   pip install anthropic --upgrade")
        print("3. Verifica tu conexión a internet")
        print(
            "4. Comprueba que el modelo solicitado esté disponible para tu cuenta")

        return None


if __name__ == "__main__":
    response = run_claude_model(
        system_prompt="You are a pirate chatbot who always responds in pirate speak!",
        user_message="Who are you?",
        model="claude-3-7-sonnet-20250219",
        max_tokens=512,
        temperature=0.7
    )