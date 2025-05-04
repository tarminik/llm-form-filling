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
        # Обновляем сессию
        for extracted in result.extracted_fields:
            field = session.fields.get(extracted.field_name)
            if field:
                field.value = extracted.value
                field.status = FieldStatus.FILLED
        # Проверяем, все ли поля заполнены
        if session.is_complete():
            session.completed = True
            return "Форма успешно заполнена!"
        else:
            missing = [name for name, field in session.fields.items() if field.status != FieldStatus.CONFIRMED]
            next_field = missing[0] if missing else None
            prompt = f"Пожалуйста, укажите значение для поля: {next_field}" if next_field else "Уточните, пожалуйста, недостающие данные."
            return prompt

    def _make_field(self, field_cfg: Dict[str, Any]):
        from app.models import FormField
        return FormField(name=field_cfg["name"])
