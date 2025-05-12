"""
CLI-интерфейс для запуска диалогового заполнения форм.
"""
import argparse
import sys
from pathlib import Path
from app.dialog_manager import DialogManager


def main():
    parser = argparse.ArgumentParser(description="LLM-форма заполнения")
    parser.add_argument("-f", "--form", required=True, help="Имя JSON-файла формы (в папке forms/)")
    args = parser.parse_args()

    form_path = Path("forms") / args.form
    if not form_path.exists():
        print(f"Форма '{args.form}' не найдена в каталоге forms/.")
        sys.exit(1)

    try:
        dialog = DialogManager(str(form_path))
        dialog.run()
    except Exception as e:
        print(f"Ошибка при запуске диалога: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
