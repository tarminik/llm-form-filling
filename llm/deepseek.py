"""
Реализация LLM-провайдера для DeepSeek.
"""
import os
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from llm.base import LLMBase

# Загружаем переменные окружения для DeepSeek
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")
if not (DEEPSEEK_API_KEY and DEEPSEEK_API_URL):
    raise RuntimeError("Ошибка конфигурации: проверьте, что DEEPSEEK_API_KEY и DEEPSEEK_API_URL заданы в .env")

class DeepSeekLLM(LLMBase):
    """
    Класс для работы с DeepSeek LLM через API.
    Реализует интерфейс LLMBase.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DEEPSEEK_API_KEY
        assert self.api_key, "Не найден API-ключ DeepSeek!"

    def ask(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024
    ) -> str:
        """
        Отправляет сообщения в DeepSeek LLM и возвращает ответ.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        try:
            response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка при обращении к DeepSeek API: {e}")
        except (KeyError, IndexError):
            raise ValueError("Ответ от LLM некорректен или неполон") 