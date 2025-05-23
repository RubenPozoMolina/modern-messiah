import logging

from mm.llama_chat_bot import LlamaChatbot

def setup_logging(log_level=logging.INFO):
    """Configure logging for the application."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('modern_messiah')

def main():
    system_file = "tests/data/system.txt"
    with open(system_file, "r") as file:
        system_content = file.read()
    user_file = "tests/data/user.txt"
    with open(user_file, "r") as file:
        user_content = file.read()
    min = 2500
    max = 3000
    user_content += f"\nEl relato debe tener entre {min} y {max} palabras"
    logger = setup_logging()
    llama_chat_bot = LlamaChatbot(
        # model="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        system_message=system_content,
        logger=logger
    )
    generated_text = llama_chat_bot.chat(user_content)
    generated_text_words = llama_chat_bot.count_words(generated_text)
    logger.info(f"Texto generado: {generated_text}")
    logger.info(f"Palabras: {generated_text_words}")

    while generated_text_words < min or generated_text_words > max:
        message = f"El texto generado contiene {generated_text_words} palabras. Necesito que tenga entre {min} y {max} palabras."
        generated_text = llama_chat_bot.chat(message)
        generated_text_words = llama_chat_bot.count_words(generated_text)
        logger.info(f"Texto generado: {generated_text}")
        logger.info(f"Palabras: {generated_text_words}")


if __name__ == "__main__":
    main()