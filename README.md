# 🧠 LLM-Form Assistant

Система для пошагового диалогового заполнения форм с помощью LLM (DeepSeek). Программа адаптируется под любую форму, описанную в формате JSON, и позволяет пользователю заполнять её в текстовом чате, как будто общается с ассистентом.

---

## ⚡ Быстрый старт

1. Клонируйте репозиторий и перейдите в папку проекта:
   ```bash
   git clone https://github.com/tarminik/llm-form-filling
   cd llm-form-filling
   ```
2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` в корне проекта (см. ниже).
4. Запустите пример:
   ```bash
   python3 main.py --form passport.json
   ```

---

## ⚙️ Настройка LLM

- Получите API-ключ для DeepSeek или OpenAI.
- В корне проекта создайте файл `.env`:
  ```
  DEEPSEEK_API_KEY=your_api_key
  DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
  # или переменные для OpenAI
  ```
- Без ключа система не будет работать.

---

## 📝 Добавление своей формы

- Создайте JSON-файл по примеру из папки `forms/`.
- Положите его в папку `forms/`.
- Запустите:
  ```bash
  python3 main.py --form myform.json
  ```

---

## 💾 Структура проекта

```
.
├── app/
│   ├── dialog_manager.py   # Логика диалога, вопросы, взаимодействие с LLM
│   ├── extractor.py        # Вызов LLM, обработка и парсинг ответов
│   ├── form_loader.py      # Загрузка формы и генерация state
│   ├── models.py           # Типы данных для форм и состояния
│   └── __init__.py
├── llm/                    # Реализации работы с LLM (DeepSeek, OpenAI)
│   ├── base.py
│   ├── deepseek.py
│   ├── openai.py
│   └── __init__.py
├── forms/                  # Ваши шаблоны форм (JSON)
├── answers/                # Сохранённые результаты
├── logs/                   # Логи диалогов
├── main.py                 # Точка входа (CLI)
├── requirements.txt        # Зависимости
└── .env                    # Ключи и настройки LLM
```

---

## 📋 Формат JSON формы

```json
{
  "id": "passport",
  "title": "Паспорт гражданина РФ",
  "description": "Форма для сбора паспортных данных.",
  "fields": [
    { "name": "Фамилия", "type": "str", "required": true, "description": "Фамилия, как указана в паспорте." },
    { "name": "Гражданство", "type": "enum", "required": true, "description": "Страна гражданства.", "options": ["Россия", "Казахстан", "Беларусь"] }
  ]
}
```

---

## 🔠 Поддерживаемые типы полей

| Тип          | Описание                         |
| ------------ | -------------------------------- |
| `str`        | Свободный текст                  |
| `int`        | Целое число                      |
| `float`      | Число с точкой                   |
| `bool`       | Да / Нет                         |
| `date`       | Дата (формат `ДД.ММ.ГГГГ`)       |
| `email`      | Email-адрес                      |
| `phone`      | Телефон                          |
| `url`        | Ссылка                           |
| `enum`       | Один вариант из заданного списка |
| `multi_enum` | Несколько вариантов из списка    |
| `list_str`   | Произвольный список строк        |

> Для `enum` и `multi_enum` обязательно указывать поле `options`.

---

## 📊 Статусы заполнения полей

| Статус        | Значение                                                  |
| ------------- | --------------------------------------------------------- |
| `not_started` | Пользователь ещё не вводил значение                       |
| `filled`      | Значение получено, формат может быть не проверен          |
| `invalid`     | Значение есть, но оно не соответствует ожидаемому формату |
| `skipped`     | Пользователь пропустил необязательное поле                |

---

## 📤 Результат

После заполнения формы результат сохраняется в:

```
answers/{form_id}_{timestamp}.json
```

Пример:

```json
{
  "Фамилия": {
    "value": "Иванов",
    "status": "filled",
    "optional": false
  },
  "Гражданство": {
    "value": "Россия",
    "status": "filled",
    "optional": false
  }
}
```

---

## ⚙️ Настройка

1. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

2. Создайте файл `.env`:

   ```
   DEEPSEEK_API_KEY=your_api_key
   DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions
   ```

---

## 📌 Пример запуска

```bash
python3 main.py --form passport.json
```

---

## 📎 TODO / идеи

* Поддержка вложенных полей
* UI-обёртка (консольная или web)
* Улучшение логирования
