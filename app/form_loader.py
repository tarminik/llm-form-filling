"""
Модуль для загрузки и валидации шаблонов форм из JSON-файлов.
"""
import json
from pathlib import Path
from typing import Dict, Any
from pydantic import ValidationError
from app.models import FormField, FieldStatus

FORMS_DIR = Path(__file__).parent.parent / "forms"


def load_form_template(form_path: Path) -> Dict[str, Any]:
    """Загрузить шаблон формы из JSON-файла."""
    with open(form_path, encoding="utf-8") as f:
        data = json.load(f)
    # Валидация структуры формы (минимально)
    assert "id" in data, "В шаблоне формы должен быть id"
    assert "fields" in data, "В шаблоне формы должен быть список fields"
    for field in data["fields"]:
        assert "name" in field, "Каждое поле должно иметь name"
        assert "type" in field, f"Поле {field['name']} должно иметь type (например, str, date, list, checkbox, reference)"
        assert "required" in field, f"Поле {field['name']} должно иметь required (True/False)"
        # Описание желательно для корректной генерации вопросов LLM
        if "description" not in field:
            print(f"[WARNING] Поле {field['name']} не имеет description — вопросы LLM могут быть менее точными.")
        # Для списков и чекбоксов обязательно наличие options
        if field["type"] in ["list", "checkbox"]:
            assert "options" in field, f"Поле {field['name']} типа {field['type']} должно иметь options (варианты выбора)"
        # Для ссылочных полей обязательно указать reference_type
        if field["type"] == "reference":
            assert "reference_type" in field, f"Поле {field['name']} типа reference должно иметь reference_type (например, 'city')"
    return data


def list_form_templates() -> Dict[str, Path]:
    """Получить список всех доступных форм (id -> путь)."""
    result = {}
    if not FORMS_DIR.exists():
        return result
    for file in FORMS_DIR.glob("*.json"):
        try:
            data = load_form_template(file)
            result[data["id"]] = file
        except Exception:
            continue
    return result
