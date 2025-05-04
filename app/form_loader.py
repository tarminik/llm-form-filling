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
