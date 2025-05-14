"""
Реализация LLM-провайдера для OpenAI.
Максимально использует универсальный базовый класс LLMBase.
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from llm.base import LLMBase

# Загружаем переменные окружения для OpenAI
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL")  # Например, https://api.openai.com/v1/chat/completions
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
if not (OPENAI_API_KEY and OPENAI_API_URL):
    raise RuntimeError("Ошибка конфигурации: проверьте, что OPENAI_API_KEY и OPENAI_API_URL заданы в .env")

class OpenAILLM(LLMBase):
    """
    Класс для работы с OpenAI LLM через API.
    Реализует только специфичные методы.
    """
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, model: Optional[str] = None):
        super().__init__(
            api_url=api_url or OPENAI_API_URL,
            api_key=api_key or OPENAI_API_KEY,
            model=model or OPENAI_MODEL
        )

    def build_payload(self, messages, temperature, max_tokens):
        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

    def build_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def parse_response(self, data):
        # OpenAI возвращает OpenAI-совместимый формат
        return data["choices"][0]["message"]["content"] 