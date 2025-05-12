"""
DialogManager — основной управляющий класс диалога заполнения формы.
Оркестрирует загрузку формы, цикл опроса пользователя, взаимодействие с LLM и сохранение результата.
"""

from typing import Optional
from app.models import Form, FormState
from datetime import datetime

class DialogManager:
    """
    Управляет процессом диалогового заполнения формы:
    - Загружает и валидирует форму
    - Инициализирует state
    - Ведёт цикл опроса пользователя
    - Взаимодействует с LLM через extractor
    - Сохраняет результат
    """
    def __init__(self, form_path: str):
        """
        Инициализация менеджера:
        - Загружает форму по пути
        - Создаёт начальный state
        - Формирует путь для сохранения результата
        """
        # ... здесь будет загрузка формы и state ...
        self.form: Optional[Form] = None
        self.state: Optional[FormState] = None
        self.form_id: Optional[str] = None
        self.form_path = form_path
        # Формируем путь для сохранения результата заранее
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = f"answers/{{form_id}}_{timestamp}.json"  # form_id подставится после загрузки формы

    def run(self):
        """
        Основной цикл диалога:
        - Пока есть незаполненные/невалидные поля, спрашивает пользователя
        - Обновляет state через extractor
        - После заполнения вызывает confirm_answers
        - Если подтверждено — сохраняет результат
        """
        pass

    def ask_user(self, field_name: str) -> str:
        """
        Задаёт вопрос пользователю по имени поля и получает ответ (input).
        Возвращает строку-ответ пользователя.
        """
        pass

    def confirm_answers(self) -> bool:
        """
        Показывает пользователю сводку всех ответов и просит подтверждение.
        Возвращает True, если пользователь подтверждает, иначе False.
        """
        pass

    def save_result(self):
        """
        Сохраняет финальный state в папку answers/ с уникальным именем.
        """
        pass

    def get_next_field(self) -> Optional[str]:
        """
        Возвращает имя следующего поля для заполнения (или None, если всё заполнено).
        В будущем сюда можно добавить более сложную логику выбора.
        """
        pass
