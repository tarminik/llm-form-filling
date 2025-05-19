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
from app.models import Form, FormState, FieldStatus
from llm import get_llm  # Используем универсальный выбор LLM-провайдера

llm = get_llm()  # Теперь провайдер выбирается через .env (LLM_PROVIDER)

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
) -> tuple[FormState, str]:
    """
    Отправляет историю, форму и state в LLM.
    Возвращает кортеж: (обновлённый FormState, next_question).
    log_callback: функция для логирования событий (role, content)
    """

    system_prompt = (
        "Ты — ассистент, помогающий пользователю заполнить форму. "
        "Форма описана ниже в формате JSON. "
        "Пользователь отвечает на вопросы, иногда указывая сразу несколько значений. "
        "Твоя задача — обновить состояния всех полей (добавить значения и статусы), которые можно заполнить по новому сообщению. "
        "Поддерживаемые статусы: not_started, filled, invalid, skipped. "
        "Если значение поля подходит — установи статус filled. "
        "Если оно некорректно (например, нарушен формат или сомнительное значение) — установи статус invalid. "
        "Нельзя менять поля со статусами filled или skipped, если пользователь явно не просит это сделать. "
        "Если хотя бы одно поле получило статус invalid — в ключ 'next_question' запиши уточняющий вопрос, относящийся к одному из таких полей. "
        "Если все поля валидны или нераспознаны — ключ 'next_question' должен быть null. "
        "Если значение можно интерпретировать, но оно указано в нестандартной форме (например, '23-12-2002', '23 декабря 2002' или 'декабрь'), преобразуй его к требуемому формату из описания поля (например, '23.12.2002' или '12') и установи статус filled. "
        "Не помечай такие значения как invalid, если их можно однозначно нормализовать. "
        "Ответ должен строго соответствовать формату JSON — объект с двумя ключами: "
        "'state' (словарь name → {value, status, optional}) и 'next_question' (строка или null). "
        "Пример:\n"
        '{"state": {"Фамилия": {"value": "Иванов", "status": "filled", "optional": false}}, "next_question": null} '
        "Никаких пояснений, комментариев или текста вне JSON — только чистый JSON-ответ."
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
    
    # First try to parse as JSON directly
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON from markdown
        cleaned = extract_json_from_markdown(response)
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as e:
            if log_callback:
                log_callback("error", f"LLM вернула не JSON: {response!r}")
            raise ValueError(
                f"LLM вернула не JSON, а текст: {response!r}\n"
                "Возможно, LLM сбилась с инструкции. Попробуйте повторить ввод или перезапустить диалог."
            )
    
    # Validate response structure
    if not isinstance(parsed, dict):
        raise ValueError("LLM вернула не объект JSON")
        
    if "state" not in parsed:
        raise ValueError("В ответе LLM отсутствует ключ 'state'")
        
    if "next_question" not in parsed:
        raise ValueError("В ответе LLM отсутствует ключ 'next_question'")
        
    if not isinstance(parsed["state"], dict):
        raise ValueError("Ключ 'state' должен быть объектом")
        
    if not isinstance(parsed["next_question"], (str, type(None))):
        raise ValueError("Ключ 'next_question' должен быть строкой или null")
        
    # Validate each field's state
    updated_state: FormState = {}
    
    # Check that all form fields are present in the response
    form_field_names = {field["name"] for field in form["fields"]}
    response_field_names = set(parsed["state"].keys())
    if not form_field_names.issubset(response_field_names):
        missing = form_field_names - response_field_names
        raise ValueError(f"В ответе LLM отсутствуют поля: {missing}")
        
    for field_name, field_state in parsed["state"].items():
        if not isinstance(field_state, dict):
            raise ValueError(f"Состояние поля '{field_name}' должно быть объектом")
            
        required_keys = {"value", "status", "optional"}
        if not required_keys.issubset(field_state):
            missing = required_keys - field_state.keys()
            raise ValueError(f"В состоянии поля '{field_name}' отсутствуют ключи: {missing}")
            
        if not isinstance(field_state["optional"], bool):
            raise ValueError(f"Ключ 'optional' поля '{field_name}' должен быть булевым")
            
        if field_state["status"] not in [status.value for status in FieldStatus]:
            raise ValueError(f"Недопустимый статус поля '{field_name}': {field_state['status']}")
            
        updated_state[field_name] = field_state
        
    next_question: str = parsed["next_question"]
    return updated_state, next_question
