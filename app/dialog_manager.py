"""
Модуль управления диалогом для поэтапного заполнения формы.
"""
import uuid
from typing import Dict, Any, Tuple
from app.models import Conversation, FormSession, Message, MessageRole, FieldStatus
from app.extractor import FormExtractor

class DialogManager:
    def __init__(self, form_config: Dict[str, Any]):
        self.form_config = form_config
        self.extractor = FormExtractor(form_config)

    def start_conversation(self) -> Tuple[Conversation, FormSession, str]:
        conversation = Conversation(id=str(uuid.uuid4()))
        session = FormSession(
            id=str(uuid.uuid4()),
            form_id=self.form_config["id"],
            fields={field["name"]: self._make_field(field) for field in self.form_config["fields"]},
            conversation_id=conversation.id
        )
        greeting = f"Давайте заполним форму: {self.form_config.get('title', self.form_config['id'])}"
        return conversation, session, greeting

    def process_user_message(self, message: str, conversation: Conversation, session: FormSession) -> str:
        # Добавляем сообщение пользователя
        conversation.add_message(MessageRole.USER, message)
        # Извлекаем поля
        result = self.extractor.extract_fields(message, session)
        # Обновляем сессию и валидируем значения
        invalid_fields = []
        for extracted in result.extracted_fields:
            field = session.fields.get(extracted.field_name)
            if field:
                # Валидация значения по типу поля
                valid, error_msg = self._validate_field_value(field, extracted.value)
                if valid:
                    field.value = extracted.value
                    field.status = FieldStatus.FILLED
                else:
                    field.status = FieldStatus.INVALID
                    invalid_fields.append((field.name, error_msg or field.description or "Введите корректное значение."))
        # Проверяем, все ли обязательные поля заполнены корректно
        required_fields = [f for f in session.fields.values() if f.required]
        if all(f.status == FieldStatus.FILLED for f in required_fields):
            session.completed = True
            return self._build_confirmation(session)
        # Если есть некорректные поля — уточняем только их
        if invalid_fields:
            questions = [f"Пожалуйста, уточните поле '{name}': {desc}" for name, desc in invalid_fields]
            return "\n".join(questions)
        # Иначе спрашиваем следующее обязательное поле
        missing = [f for f in required_fields if f.status != FieldStatus.FILLED]
        if missing:
            next_field = missing[0]
            prompt = f"Пожалуйста, укажите значение для поля: {next_field.name} ({next_field.description or ''})"
            return prompt
        return "Уточните, пожалуйста, недостающие данные."

    def _validate_field_value(self, field, value):
        """
        Валидация значения по типу поля. Возвращает (True/False, сообщение об ошибке).
        """
        t = field.type
        if t == "str":
            if not value or not str(value).strip():
                return False, "Поле не должно быть пустым."
            # Спец. правила для номера/серии паспорта
            if "номер" in field.name.lower() and (not str(value).isdigit() or len(str(value)) != 6):
                return False, "Номер паспорта должен состоять из 6 цифр."
            if "серия" in field.name.lower() and (not str(value).isdigit() or len(str(value)) != 4):
                return False, "Серия паспорта должна состоять из 4 цифр."
            return True, None
        elif t == "date":
            import re
            if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", str(value)):
                return False, "Дата должна быть в формате ДД.ММ.ГГГГ."
            return True, None
        elif t in ["list", "checkbox"]:
            if field.options and value not in field.options:
                return False, f"Значение должно быть одним из: {', '.join(field.options)}."
            return True, None
        elif t == "reference":
            if not value or not str(value).strip():
                return False, "Поле не должно быть пустым."
            # Можно добавить логику поиска по справочнику
            return True, None
        return True, None

    def _build_confirmation(self, session: FormSession) -> str:
        """
        Формирует итоговое подтверждение для пользователя.
        """
        data = session.get_filled_data()
        lines = ["Проверьте заполненные данные:"]
        for k, v in data.items():
            lines.append(f"- {k}: {v}")
        lines.append("Если всё верно, напишите 'да'. Если нужно что-то исправить — укажите поле и новое значение.")
        return "\n".join(lines)

    def _make_field(self, field_cfg: Dict[str, Any]):
        from app.models import FormField
        # Передаём все параметры поля для поддержки новых атрибутов
        return FormField(**field_cfg)

