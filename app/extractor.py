"""
extractor.py — взаимодействие с LLM для обновления состояния формы на основе истории диалога.
"""
from typing import List, Dict
from app.models import Form, FormState
from app.llm_service import LLMService
import json


def extract_fields(
    messages: List[Dict[str, str]],
    form: Form,
    state: FormState
) -> FormState:
    """
    Отправляет всю историю общения, форму и state в LLM.
    Возвращает обновлённый state.

    messages: список сообщений (system, assistant, user) в хронологическом порядке.
    form: структура формы (dict).
    state: текущее состояние (dict).

    Пример структуры messages:
    [
        {"role": "system", "content": "...инструкция и JSON формы+state..."},
        {"role": "assistant", "content": "Введите значение поля 'Имя'."},
        {"role": "user", "content": "Иван"},
        ...
    ]

    Важно:
    - В system prompt сериализовать form и state (или добавить отдельным сообщением).
    - После вызова LLM валидировать, что ответ — корректный JSON с обновлённым state.
    """
    # 1. Сформировать system prompt с формой и state
    # 2. Добавить историю сообщений
    # 3. Вызвать LLMService.ask(messages)
    # 4. Распарсить ответ, проверить структуру
    # 5. Вернуть обновлённый state
    pass
