import json
import pytest
from pathlib import Path
from app.dialog_manager import DialogManager

def test_get_next_field_returns_first_not_started(forms_dir):
    """Test that get_next_field returns the first field with not_started status."""
    dm = DialogManager(form_path=str(forms_dir / "email.json"))
    
    # Get the actual field names from the form
    field_names = list(dm.state.keys())
    if len(field_names) < 2:
        pytest.skip("Form must have at least 2 fields for this test")
    
    # Manually set statuses to test the function
    dm.state[field_names[0]]["status"] = "filled"
    dm.state[field_names[1]]["status"] = "not_started"
    
    # Should return the first not_started field
    assert dm.get_next_field() == field_names[1]

def test_get_next_field_returns_none_when_all_filled(forms_dir):
    """Test that get_next_field returns None when all fields are filled."""
    dm = DialogManager(form_path=str(forms_dir / "email.json"))
    
    # Set all fields to filled
    for field in dm.state:
        dm.state[field]["status"] = "filled"
    
    assert dm.get_next_field() is None

def test_confirm_answers_yes(monkeypatch, forms_dir):
    """Test confirm_answers with 'yes' input."""
    # Mock input to return 'yes'
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    
    dm = DialogManager(form_path=str(forms_dir / "email.json"))
    field_name = list(dm.state.keys())[0]  # Get first field name
    dm.state[field_name] = {
        "status": "filled",
        "value": "test@example.com",
        "optional": False
    }
    
    assert dm.confirm_answers() is True

def test_confirm_answers_no(monkeypatch, forms_dir):
    """Test confirm_answers with 'no' input."""
    # Mock input to return 'no'
    monkeypatch.setattr('builtins.input', lambda _: 'no')
    
    dm = DialogManager(form_path=str(forms_dir / "email.json"))
    field_name = list(dm.state.keys())[0]  # Get first field name
    dm.state[field_name] = {
        "status": "filled",
        "value": "test@example.com",
        "optional": False
    }
    
    assert dm.confirm_answers() is False

def test_save_result(tmp_path, forms_dir):
    """Test that save_result creates a file with correct JSON structure."""
    # Set up output directory
    output_dir = tmp_path / "answers"
    output_dir.mkdir()
    
    # Initialize dialog manager and set some state
    dm = DialogManager(form_path=str(forms_dir / "email.json"))
    field_name = list(dm.state.keys())[0]  # Get first field name
    dm.state[field_name] = {
        "status": "filled",
        "value": "test@example.com",
        "optional": False
    }
    
    # Override output path for testing
    dm.output_path = str(output_dir / "test_result.json")
    
    # Save the result
    dm.save_result()
    
    # Verify file exists and contains correct JSON
    assert Path(dm.output_path).exists()
    saved_data = json.loads(Path(dm.output_path).read_text())
    
    # Verify the saved state matches what we set
    assert field_name in saved_data
    assert saved_data[field_name]["status"] == "filled"
    assert saved_data[field_name]["value"] == "test@example.com"
    assert saved_data[field_name]["optional"] is False 