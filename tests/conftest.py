"""
Test fixtures and mocks.
"""
import os
import shutil
from pathlib import Path
import pytest
from app.extractor import extract_fields, extract_json_from_markdown
from llm import get_llm

@pytest.fixture
def forms_dir(tmp_path):
    """Create a temporary directory with test form files."""
    # Create a temporary directory
    forms_path = tmp_path / "forms"
    forms_path.mkdir()
    
    # Copy test forms from the real forms directory
    real_forms_dir = Path("forms")
    for form_file in real_forms_dir.glob("*.json"):
        shutil.copy2(form_file, forms_path / form_file.name)
    
    return forms_path

@pytest.fixture
def mock_llm(monkeypatch):
    """Mock LLM class that returns predefined responses."""
    class MockLLM:
        def __init__(self):
            self.responses = {
                # Valid response with filled status
                "default": '{"state": {"Фамилия": {"value": "Иванов", "status": "filled", "optional": false}}, "next_question": null}',
                # Invalid JSON response
                "invalid_json": "This is not a JSON response at all",
                # Response with missing required field (optional)
                "missing_field": '{"state": {"Фамилия": {"value": "Иванов", "status": "filled"}}, "next_question": null}',
                # Response with test prompt
                "test_prompt": '{"state": {"Фамилия": {"value": "Test prompt", "status": "filled", "optional": false}}, "next_question": null}',
                # Response with invalid status
                "invalid_status": '{"state": {"Фамилия": {"value": "Иванов", "status": "invalid", "optional": false}}, "next_question": "Пожалуйста, введите корректную фамилию"}'
            }
            self.current_response = "default"
        
        def set_response(self, response_key):
            """Set which predefined response to return."""
            if response_key not in self.responses:
                raise ValueError(f"Unknown response key: {response_key}")
            self.current_response = response_key
            
        def ask(self, messages):
            """Return the current predefined response."""
            return self.responses[self.current_response]
    
    mock = MockLLM()
    # Mock the get_llm function to return our mock LLM
    monkeypatch.setattr("llm.get_llm", lambda: mock)
    return mock

@pytest.fixture
def sample_form_json():
    """Return a minimal valid form JSON for testing."""
    return {
        "id": "test_form",
        "title": "Test Form",
        "description": "A test form for unit testing",
        "fields": [
            {
                "name": "Фамилия",
                "type": "str",
                "required": True,
                "description": "Введите вашу фамилию"
            },
            {
                "name": "Имя",
                "type": "str",
                "required": True,
                "description": "Введите ваше имя"
            }
        ]
    } 