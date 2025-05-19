import json
import pytest
from pathlib import Path
from app.form_loader import load_form, init_state

def test_load_form_ok(tmp_path, sample_form_json):
    """Test loading a valid form JSON file."""
    # Create a temporary form file
    form_path = tmp_path / "test_form.json"
    form_path.write_text(json.dumps(sample_form_json))
    
    # Load the form
    form = load_form(str(form_path))
    
    # Verify the form structure
    assert "fields" in form
    assert len(form["fields"]) > 0
    assert any(field["name"] == "Фамилия" for field in form["fields"])
    assert any(field["name"] == "Имя" for field in form["fields"])

def test_load_form_missing_key(tmp_path):
    """Test loading a form with missing required key."""
    # Create an invalid form without 'fields' key
    invalid_form = {"some_other_key": "value"}
    form_path = tmp_path / "invalid_form.json"
    form_path.write_text(json.dumps(invalid_form))
    
    # Attempt to load the form
    with pytest.raises(ValueError, match="Форма некорректна, отсутствуют ключи"):
        load_form(str(form_path))

def test_load_form_bad_field_type(tmp_path):
    """Test loading a form with invalid field type."""
    # Create a form with invalid field type
    invalid_form = {
        "id": "test_form",
        "title": "Test Form",
        "description": "A test form",
        "fields": [
            {
                "name": "Фамилия",
                "type": "invalid_type",  # Invalid type
                "required": True,
                "description": "Test"
            }
        ]
    }
    form_path = tmp_path / "invalid_type_form.json"
    form_path.write_text(json.dumps(invalid_form))
    
    # Attempt to load the form
    with pytest.raises(ValueError, match="Недопустимый тип поля"):
        load_form(str(form_path))

def test_init_state_defaults(tmp_path, sample_form_json):
    """Test that init_state creates correct default state."""
    # Create a temporary form file
    form_path = tmp_path / "test_form.json"
    form_path.write_text(json.dumps(sample_form_json))
    
    # Load the form and initialize state
    form = load_form(str(form_path))
    state = init_state(form)
    
    # Verify state structure
    assert "Фамилия" in state
    assert "Имя" in state
    
    # Check each field's default state
    for field in form["fields"]:
        field_name = field["name"]
        assert field_name in state
        field_state = state[field_name]
        assert "status" in field_state
        assert field_state["status"] == "not_started"
        assert "optional" in field_state
        assert field_state["optional"] == (not field["required"])
        assert field_state["value"] is None  # Value should be None initially 