import pytest
import copy
from src.common.config import Config

def test_config_root_validation(tmp_path):
    # Test that loading a non-dict JSON (e.g. list) raises TypeError
    list_config = tmp_path / "list_config.json"
    list_config.write_text('[1, 2, 3]')
    with pytest.raises(TypeError, match="Config root must be a JSON object"):
        Config(str(list_config))

    # Test that loading a valid dict JSON works
    dict_config = tmp_path / "dict_config.json"
    dict_config.write_text('{"key": "value"}')
    config = Config(str(dict_config))
    assert config.get("key") == "value"

def test_config_deepcopy_safety(tmp_path):
    # Test load deepcopy
    dict_config = tmp_path / "dict_config.json"
    dict_config.write_text('{"nested": {"key": "val"}}')
    config = Config(str(dict_config))
    
    # Verify we can't mutate the internal dictionary by mutating external references
    data = config.to_dict()
    data["nested"]["key"] = "mutated"
    assert config.get("nested.key") == "val"

    # Test set deepcopy
    new_nested = {"hello": "world"}
    config.set("nested_set", new_nested)
    new_nested["hello"] = "mutated"
    assert config.get("nested_set.hello") == "world"

    # Test to_dict deepcopy
    data2 = config.to_dict()
    data2["nested_set"]["hello"] = "mutated2"
    assert config.get("nested_set.hello") == "world"

def test_config_redaction():
    config = Config()
    config.set("api_key", "secret123")
    config.set("app.client_secret", "password456")
    config.set("app.token", "mytoken")
    config.set("app.safe_param", "safe")
    config.set("nested.db.password", "admin123")
    config.set("array_of_items", [{"token": "tok1"}, {"other": "safe"}])

    redacted = config.to_redacted_dict()
    
    assert redacted["api_key"] == "******"
    assert redacted["app"]["client_secret"] == "******"
    assert redacted["app"]["token"] == "******"
    assert redacted["app"]["safe_param"] == "safe"
    assert redacted["nested"]["db"]["password"] == "******"
    assert redacted["array_of_items"][0]["token"] == "******"
    assert redacted["array_of_items"][1]["other"] == "safe"

    # Verify original is untouched
    orig = config.to_dict()
    assert orig["api_key"] == "secret123"
    assert orig["app"]["client_secret"] == "password456"

