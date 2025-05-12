"""
Типы данных для формы, полей и состояний заполнения.
"""

from enum import Enum
from typing import Optional, List, Union, Literal, Dict, TypedDict

# Статусы заполнения поля
class FieldStatus(str, Enum):
    """Возможные статусы заполнения поля формы."""
    NOT_STARTED = "not_started"
    FILLED = "filled"
    INVALID = "invalid"
    SKIPPED = "skipped"

# Типы полей формы
FieldType = Literal[
    "str", "int", "float", "bool", "date",
    "email", "phone", "url", "enum", "multi_enum", "list_str"
]

# Описание одного поля в форме
class Field(TypedDict):
    """
    Описание одного поля в форме.
    options — только для enum/multi_enum, иначе отсутствует.
    """
    name: str
    type: FieldType
    required: bool
    description: str
    options: Optional[List[str]]  # Только для enum/multi_enum, иначе отсутствует

# Описание всей формы
class Form(TypedDict):
    """
    Описание всей формы: id, заголовок, описание и список полей.
    """
    id: str
    title: str
    description: str
    fields: List[Field]

# Состояние одного поля во время диалога
class FieldState(TypedDict):
    """
    Состояние одного поля: значение, статус, признак необязательности.
    """
    value: Optional[Union[str, int, float, bool, List[str]]]
    status: FieldStatus
    optional: bool

# Состояние всей формы: имя_поля → состояние
FormState = Dict[str, FieldState]
