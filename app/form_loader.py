"""
Модуль загрузки формы и генерации начального состояния.
"""

import json
from typing import Dict
from app.models import Form, Field, FormState, FieldState, FieldStatus, FieldType

def load_form(form_path: str) -> Form:
    """
    Загружает и валидирует JSON-форму по указанному пути.
    """
    with open(form_path, encoding="utf-8") as f:
        data = json.load(f)

    # Базовая проверка
    required_keys = {"id", "title", "description", "fields"}
    if not required_keys.issubset(data):
        missing = required_keys - data.keys()
        raise ValueError(f"Форма некорректна, отсутствуют ключи: {missing}")

    # Проверка полей
    for field in data["fields"]:
        if not {"name", "type", "required", "description"}.issubset(field):
            raise ValueError(f"Некорректное поле: {field}")

        if field["type"] not in FieldType.__args__:
            raise ValueError(f"Недопустимый тип поля: {field['type']}")

        if field["type"] in ("enum", "multi_enum"):
            if "options" not in field:
                raise ValueError(f"Поле типа {field['type']} должно содержать 'options'")

    return data  # тип Form

def init_state(form: Form) -> FormState:
    """
    Создаёт начальное состояние формы: value=None, status=not_started, optional по required.
    """
    state: FormState = {}

    for field in form["fields"]:
        name = field["name"]
        state[name] = {
            "value": None,
            "status": FieldStatus.NOT_STARTED,
            "optional": not field["required"]
        }

    return state
