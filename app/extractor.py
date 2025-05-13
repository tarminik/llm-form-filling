"""
Модуль extractor отвечает за взаимодействие с LLM:
- принимает текущую историю сообщений, форму и state,
- формирует system prompt,
- передаёт всё в LLM,
- получает и возвращает обновлённый state.
"""

import json
import re
from typing import List, Dict
from app.models import Form, FormState
from app.llm_service import LLMService

llm = LLMService()

def extract_json_from_markdown(text: str) -> str:
    """
    Удаляет markdown-блоки ```json ... ``` или ``` ... ``` вокруг JSON-ответа LLM.
    Возвращает чистый JSON-стринг.
    """
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def extract_fields(
    messages: List[Dict[str, str]],
    form: Form,
    state: FormState,
    log_callback=None
) -> FormState:
    """
    Отправляет историю, форму и state в LLM.
    Возвращает обновлённый FormState.
    log_callback: функция для логирования событий (role, content)
    """

    system_prompt = (
        "Ты помощник, который помогает пользователю заполнить форму. "
        "Форма описана ниже как JSON. "
        "Пользователь отвечает на вопросы, иногда сразу даёт несколько ответов. "
        "Твоя задача — по каждому новому сообщению определить, какие поля можно заполнить, "
        "и обновить их значения и статусы. "
        "Статусы полей: not_started, filled, invalid, skipped. "
        "Нельзя перезаписывать поля, у которых статус filled или skipped, кроме случаев, когда пользователь прямо вносит правку. "
        "Ты всегда возвращаешь только JSON, без пояснений, вопросов и текста. "
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
    if log_callback:
        log_callback("llm_raw", response)
    cleaned = extract_json_from_markdown(response)
    if not cleaned.strip().startswith(("{", "[")):
        if log_callback:
            log_callback("error", f"LLM вернула не JSON: {cleaned!r}")
        raise ValueError(
            f"LLM вернула не JSON, а текст: {cleaned!r}\n"
            "Возможно, LLM сбилась с инструкции. Попробуйте повторить ввод или перезапустить диалог."
        )
    try:
        updated_state: FormState = json.loads(cleaned)
        return updated_state
    except json.JSONDecodeError as e:
        if log_callback:
            log_callback("error", f"Ошибка парсинга JSON: {e}\nОтвет: {response}")
        raise ValueError(f"LLM вернула некорректный JSON: {e}\nОтвет: {response}")
