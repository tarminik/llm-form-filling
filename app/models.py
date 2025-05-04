"""
Модели данных для системы диалогового заполнения форм.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class Conversation(BaseModel):
    id: str
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: MessageRole, content: str):
        """
        Добавляет новое сообщение в диалог.
        Аргументы:
            role (MessageRole): Роль отправителя (user, assistant, system).
            content (str): Текст сообщения.
        Сообщение автоматически получает текущее время как timestamp.
        """
        msg = Message(role=role, content=content)
        self.messages.append(msg)
        self.updated_at = datetime.now()


class FieldStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FILLED = "filled"
    CONFIRMED = "confirmed"
    INVALID = "invalid"
    SKIPPED = "skipped"

class FieldValue(BaseModel):
    value: Any
    confidence: float = 1.0
    extracted_from: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)

class FormField(BaseModel):
    name: str
    type: str  # Тип поля (str, date, list, checkbox, reference и т.д.)
    required: bool = True  # Обязательное ли поле
    description: Optional[str] = None  # Описание поля для пользователя и LLM
    options: Optional[List[str]] = None  # Для списков и чекбоксов
    reference_type: Optional[str] = None  # Для ссылочных полей (например, "city")
    status: FieldStatus = FieldStatus.NOT_STARTED
    value: Optional[FieldValue] = None
    attempts: int = 0
    last_prompt: Optional[str] = None
    # Старые поля и методы оставляем для совместимости


class FormSession(BaseModel):
    id: str
    form_id: str
    fields: Dict[str, FormField] = Field(default_factory=dict)
    conversation_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False
    current_field: Optional[str] = None

    def get_filled_data(self):
        return {name: field.value.value for name, field in self.fields.items() if field.value is not None}

    def is_complete(self):
        return all(field.status == FieldStatus.CONFIRMED for field in self.fields.values())

class ExtractedField(BaseModel):
    field_name: str
    value: Any
    confidence: float
    context: Optional[str] = None

class ExtractionResult(BaseModel):
    extracted_fields: List[ExtractedField]
    missing_fields: List[str]
    ambiguous_fields: List[str]
    contradictions: List[Dict[str, Any]]
    raw_llm_response: Optional[str] = None
