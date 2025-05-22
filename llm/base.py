"""
Универсальный базовый класс для всех LLM-провайдеров.
Содержит общую логику отправки запроса и обработки ошибок.
Провайдеры должны реализовать методы build_payload, build_headers, parse_response.
"""
from typing import List, Dict, Any
from abc import ABC, abstractmethod
import requests

class LLMBase(ABC):
    def __init__(self, api_url: str, api_key: str, model: str = None):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    def ask(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024
    ) -> str:
        """
        Общий метод для отправки сообщений в LLM и получения ответа.
        """
        payload = self.build_payload(messages, temperature, max_tokens)
        headers = self.build_headers()
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            data = response.json()
            return self.parse_response(data)
        except requests.RequestException as e:
            raise RuntimeError(f"Ошибка при обращении к LLM API: {e}")
        except (KeyError, IndexError):
            raise ValueError("Ответ от LLM некорректен или неполон")

    @abstractmethod
    def build_payload(self, messages, temperature, max_tokens):
        """
        Формирует payload для конкретного API.
        Должен быть реализован в наследнике.
        """
        raise NotImplementedError

    @abstractmethod
    def build_headers(self):
        """
        Формирует headers для конкретного API.
        Должен быть реализован в наследнике.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, data):
        """
        Извлекает текст ответа из данных API.
        Должен быть реализован в наследнике.
        """
        raise NotImplementedError 