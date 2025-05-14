"""
Базовый интерфейс для всех LLM-провайдеров.
"""
from typing import List, Dict, Any

class LLMBase:
    def ask(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 1.0,
        max_tokens: int = 1024
    ) -> str:
        """
        Отправляет сообщения в LLM и возвращает ответ.
        Должен быть реализован в каждом конкретном провайдере.
        """
        raise NotImplementedError("Метод ask должен быть реализован в наследнике LLMBase.") 