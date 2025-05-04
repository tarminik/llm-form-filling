"""
Модуль для извлечения полей формы из текста сообщения с помощью LLM.
"""
from typing import List, Dict, Any
from app.llm_service import llm_service
from app.models import ExtractedField, ExtractionResult, FormSession, Message

class FormExtractor:
    def __init__(self, form_config: Dict[str, Any]):
        self.form_config = form_config
        self.field_names = [field["name"] for field in form_config["fields"]]

    def extract_fields(self, message: str, session: FormSession, context: List[Message] = None) -> ExtractionResult:
        # Формируем промпт для LLM
        prompt = self._build_prompt(message, session)
        response = llm_service.ask([
            {"role": "system", "content": "Ты помощник по заполнению форм. Отвечай только на русском."},
            {"role": "user", "content": prompt}
        ])
        # Здесь предполагается, что LLM возвращает JSON с заполненными полями
        try:
            data = self._parse_response(response)
        except Exception:
            data = {}
        extracted = []
        for field in self.field_names:
            if field in data:
                extracted.append(ExtractedField(field_name=field, value=data[field], confidence=1.0))
        missing = [f for f in self.field_names if f not in data]
        return ExtractionResult(
            extracted_fields=extracted,
            missing_fields=missing,
            ambiguous_fields=[],
            contradictions=[],
            raw_llm_response=response
        )

    def _build_prompt(self, message: str, session: FormSession) -> str:
        fields_list = ", ".join(self.field_names)
        return (
            f"Пользователь написал: {message}\n"
            f"Извлеки значения для следующих полей формы: {fields_list}. "
            "Ответь в формате JSON: {\"<название поля>\": <значение>, ...}"
        )

    def _parse_response(self, response: str) -> Dict[str, Any]:
        import json
        return json.loads(response)
