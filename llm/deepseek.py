"""
Реализация LLM-провайдера для DeepSeek.
Максимально использует универсальный базовый класс LLMBase.
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from llm.base import LLMBase

# Загружаем переменные окружения для DeepSeek
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

if not (DEEPSEEK_API_KEY and DEEPSEEK_API_URL):
    raise RuntimeError("Ошибка конфигурации: проверьте, что DEEPSEEK_API_KEY и DEEPSEEK_API_URL заданы в .env")

class DeepSeekLLM(LLMBase):
    """
    Класс для работы с DeepSeek LLM через API.
    Реализует только специфичные методы.
    """
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None, model: Optional[str] = None):
        super().__init__(
            api_url=api_url or DEEPSEEK_API_URL,
            api_key=api_key or DEEPSEEK_API_KEY,
            model=model or DEEPSEEK_MODEL
        )

    def build_payload(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

    def build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def parse_response(self, data: Dict[str, Any]) -> str:
        # DeepSeek возвращает OpenAI-совместимый формат
        return data["choices"][0]["message"]["content"] 