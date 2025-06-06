"""
DialogManager — основной управляющий класс диалога заполнения формы.
Оркестрирует загрузку формы, цикл опроса пользователя, взаимодействие с LLM и сохранение результата.
"""

import os
import time
from typing import Optional
from app.models import Form, FormState
from app import form_loader
from app.extractor import extract_fields
import json
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
        - Подготавливает путь сохранения ответа
        """
        self.form: Form = form_loader.load_form(form_path)
        self.state: FormState = form_loader.init_state(self.form)
        self.messages: list[dict[str, str]] = []

        # Уникальное имя результата
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        form_id = self.form["id"]
        self.output_path = os.path.join("answers", f"{form_id}_{timestamp}.json")
        self.log_path = os.path.join("logs", f"{form_id}_{timestamp}_log.json")
        self.log = []  # Список событий для логгирования
        print(f"Форма загружена: {self.form['title']}")

    def log_event(self, role: str, content: str):
        """
        Добавляет событие в лог с таймстемпом.
        role: 'user', 'assistant', 'llm', 'error'
        content: текст сообщения или JSON-ответа
        """
        self.log.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "role": role,
            "content": content
        })

    def run(self):
        """
        Основной цикл диалога:
        - Пока есть незаполненные/невалидные поля, спрашивает пользователя
        - Обновляет state через extractor
        - После заполнения вызывает confirm_answers
        - Если подтверждено — сохраняет результат
        """

        # Логируем используемую модель LLM при старте диалога
        try:
            from app.extractor import llm
            self.log_event("llm", f"Используется LLM-модель: {llm.__class__.__name__} (model={getattr(llm, 'model', 'unknown')})")
        except Exception as e:
            self.log_event("error", f"Не удалось определить модель LLM: {e}")

        print("\nНачинаем заполнение формы. Для выхода в любой момент введите 'выход'.\n")

        next_question = None
        first_run = True
        while True:
            if first_run:
                # Для первого вопроса: спрашиваем по get_next_field
                self.messages = []
                next_field = self.get_next_field()
                if next_field is None:
                    print("\nНет полей для заполнения.")
                    break
                next_question = f"Введите значение поля '{next_field}':"
                first_run = False
            else:
                # После каждого ответа вызываем extract_fields
                try:
                    self.state, next_question = extract_fields(self.messages, self.form, self.state, log_callback=self.log_event)
                except Exception as e:
                    err = f"Ошибка при обработке ответа LLM: {e}"
                    print(err)
                    self.log_event("error", err)
                    continue

                # Если нет полей invalid, формируем вопрос кодом
                invalid_fields = [name for name, field in self.state.items() if field["status"] == "invalid"]
                if not invalid_fields:
                    next_field = self.get_next_field()
                    if next_field is None:
                        print("\nВсе поля заполнены или пропущены.")
                        if self.confirm_answers():
                            self.save_result()
                            print(f"\nРезультат сохранён в {self.output_path}")
                            break
                        else:
                            # Пользователь хочет внести исправления
                            correction = input("\nУточните, что нужно изменить: ")
                            if correction.strip().lower() == "выход":
                                print("Выход без сохранения.")
                                break
                            self.log_event("user", correction)
                            self.messages.append({"role": "user", "content": correction})
                            continue
                    next_question = f"Введите значение поля '{next_field}':"
                # иначе next_question уже содержит уточняющий вопрос от LLM

            print(next_question)
            user_input = input("> ")
            if user_input.strip().lower() == "выход":
                print("Выход без сохранения.")
                break

            self.log_event("assistant", next_question)
            self.log_event("user", user_input)
            self.messages.append({"role": "assistant", "content": next_question})
            self.messages.append({"role": "user", "content": user_input})

    def ask_user(self, field_name: str) -> str:
        """
        Задаёт вопрос пользователю по имени поля и получает ответ.
        """
        return input(f">>> Введите значение поля '{field_name}': ")

    def confirm_answers(self) -> bool:
        """
        Показывает пользователю текущие значения и просит подтверждение.
        """
        print("\n--- Проверка заполненных данных ---")
        for name, field in self.state.items():
            if field["status"] == "filled":
                print(f"{name}: {field['value']}")
            elif field["status"] == "skipped":
                print(f"{name}: <пропущено>")
        print("-----------------------------------")

        response = input("Все данные верны? (да/нет): ").strip().lower()
        return response in ["да", "yes", "ок", "всё верно", "подтверждаю"]

    def save_result(self):
        """
        Сохраняет итоговый state в JSON-файл в папке answers.
        """
        os.makedirs("answers", exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        os.makedirs("logs", exist_ok=True)
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, ensure_ascii=False, indent=2)

    def get_next_field(self) -> Optional[str]:
        """
        Возвращает имя следующего поля для заполнения (или None, если всё заполнено/пропущено).
        """
        for name, field in self.state.items():
            if field["status"] in ["not_started", "invalid"]:
                return name
        return None
