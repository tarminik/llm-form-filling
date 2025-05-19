import subprocess
import pytest
from pathlib import Path
import os
import sys

# Определяем абсолютный путь к main.py (в корне проекта) для запуска тестов CLI
MAIN_PY = str(Path(__file__).parent.parent / "main.py")

def test_main_with_existing_form(forms_dir):
    """Test that main.py exits with code 0 when form exists."""
    form_path = forms_dir / "email.json"
    result = subprocess.run(
        [sys.executable, MAIN_PY, "-f", str(form_path)],
        cwd=str(forms_dir.parent),
        input="test@example.com\nТестовая тема\nТекст письма\nда\n",
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 0

def test_main_with_nonexistent_form(forms_dir):
    """Test that main.py exits with code 1 when form doesn't exist."""
    form_path = forms_dir / "nonexistent.json"
    result = subprocess.run(
        [sys.executable, MAIN_PY, "-f", str(form_path)],
        cwd=str(forms_dir.parent),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode == 1
    assert "не найдена" in result.stdout

def test_main_with_invalid_form(forms_dir, tmp_path):
    """Test that main.py handles invalid form gracefully."""
    invalid_form = tmp_path / "invalid.json"
    invalid_form.write_text("This is not valid JSON")
    result = subprocess.run(
        [sys.executable, MAIN_PY, "-f", str(invalid_form)],
        cwd=str(forms_dir.parent),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    assert result.returncode != 0
    assert "ошибка" in result.stdout.lower() 