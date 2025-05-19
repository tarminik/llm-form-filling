import pytest
from app.extractor import extract_json_from_markdown, extract_fields
from app.models import Form

@pytest.fixture
def sample_form():
    """Return a minimal form for testing."""
    return {
        "id": "test_form",
        "title": "Test Form",
        "description": "A test form",
        "fields": [
            {
                "name": "Фамилия",
                "type": "str",
                "required": True,
                "description": "Введите фамилию"
            }
        ]
    }

@pytest.mark.parametrize("raw,expected", [
    ("```json\n{\"a\":1}\n```", '{"a":1}'),
    ('{"a":1}', '{"a":1}'),
    ('```json\n{"a":1,"b":2}\n```', '{"a":1,"b":2}'),
    ('{"a":1,"b":2}', '{"a":1,"b":2}'),
])
def test_strip_markdown(raw, expected):
    """Test JSON extraction from markdown and raw JSON."""
    assert extract_json_from_markdown(raw) == expected

def test_extract_fields_next_question_none(mock_llm, sample_form):
    """Test that next_question is None when all fields are filled."""
    # Initial state with one field
    initial_state = {
        "Фамилия": {
            "status": "not_started",
            "optional": False
        }
    }
    
    # Extract fields
    new_state, next_question = extract_fields(
        messages=[{"role": "user", "content": "Test prompt"}],
        form=sample_form,
        state=initial_state
    )
    
    # Verify next_question is None
    assert next_question is None 