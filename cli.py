"""
CLI-интерфейс для запуска диалогового заполнения форм.
"""
import argparse
from pathlib import Path
from app.form_loader import list_form_templates, load_form_template
from app.dialog_manager import DialogManager


def main():
    parser = argparse.ArgumentParser(description="Диалоговое заполнение форм с помощью LLM")
    parser.add_argument("--form", type=str, help="ID формы для заполнения")
    args = parser.parse_args()

    forms = list_form_templates()
    if not forms:
        print("Не найдено ни одной формы. Поместите JSON-шаблоны в папку code/forms/")
        return

    form_id = args.form
    if not form_id or form_id not in forms:
        print("Доступные формы:")
        for fid in forms:
            print(f"- {fid}")
        form_id = input("Введите id формы для заполнения: ").strip()
        if form_id not in forms:
            print("Форма не найдена!")
            return

    form_cfg = load_form_template(forms[form_id])
    manager = DialogManager(form_cfg)
    conversation, session, greeting = manager.start_conversation()
    print(greeting)
    while not session.completed:
        user_msg = input("Вы: ")
        reply = manager.process_user_message(user_msg, conversation, session)
        print(f"Ассистент: {reply}")
    print("\nРезультаты заполнения:")
    print(session.get_filled_data())

if __name__ == "__main__":
    main()
