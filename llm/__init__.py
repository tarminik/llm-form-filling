import os
from dotenv import load_dotenv

load_dotenv()

from llm.openai import OpenAILLM
from llm.deepseek import DeepSeekLLM


def get_llm():
    """
    Возвращает экземпляр LLM-класса в зависимости от переменной окружения LLM_PROVIDER.
    Поддерживаемые значения: 'openai', 'deepseek'.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Можно легко добавить новых провайдеров в этот словарь
    providers = {
        "openai": OpenAILLM,
        "deepseek": DeepSeekLLM,
    }

    if provider not in providers:
        raise ValueError(f"LLM_PROVIDER '{provider}' не поддерживается. Доступные: {list(providers.keys())}")

    # Возвращаем экземпляр выбранного LLM
    return providers[provider]()

# Пример использования:
# llm = get_llm()
# response = llm.generate(messages=[...]) 