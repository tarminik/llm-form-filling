"""
Модуль extractor отвечает за взаимодействие с LLM:
- принимает текущую историю сообщений, форму и state,
- формирует system prompt,
- передаёт всё в LLM,
- получает и возвращает обновлённый state.
"""

import json
from typing import List, Dict
from app.models import Form, FormState
from app.llm_service import LLMService

llm = LLMService()

def extract_fields(
    messages: List[Dict[str, str]],
    form: Form,
    state: FormState
) -> FormState:
    """
    Отправляет историю, форму и state в LLM.
    Возвращает обновлённый FormState.
    """

    system_prompt = (
        "Ты помощник, который помогает пользователю заполнить форму. "
        "Форма описана ниже как JSON. "
        "Пользователь отвечает на вопросы, иногда сразу даёт несколько ответов. "
        "Твоя задача — по каждому новому сообщению определить, какие поля можно заполнить, "
        "и обновить их значения и статусы. "
        "Статусы полей: not_started, filled, invalid, skipped. "
        "Нельзя перезаписывать поля, у которых статус filled или skipped, кроме случаев, когда пользователь прямо вносит правку. "
        "Верни только JSON с обновлённым state (в формате name: {value, status, optional}), без пояснений или комментариев."
    )

    full_messages = [{"role": "system", "content": system_prompt}]
    full_messages += messages

    full_messages.append({
        "role": "system",
        "content": (
            "Вот описание формы:\n"
            f"{json.dumps(form, ensure_ascii=False, indent=2)}\n\n"
            "Вот текущее состояние state:\n"
            f"{json.dumps(state, ensure_ascii=False, indent=2)}"
        )
    })

    response = llm.ask(full_messages)
    
    try:
        updated_state: FormState = json.loads(response)
        return updated_state
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM вернула некорректный JSON: {e}\nОтвет: {response}")
