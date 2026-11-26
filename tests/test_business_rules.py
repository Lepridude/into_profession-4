import importlib.util
from pathlib import Path
from unittest.mock import patch
import pytest

path = Path(__file__).resolve().parents[1] / "business-rules.py"
spec = importlib.util.spec_from_file_location("business_rules", path)
rules = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)

class Response:
    def __init__(self, data): self.data = data
    def raise_for_status(self): pass
    def json(self): return self.data

def test_check_user_true():
    with patch.object(rules.requests, "post", return_value=Response({"DataSet":{"Rows":[{"user_exists":1}]}})):
        assert rules._check_user_id(1) is True

def test_check_user_false():
    with patch.object(rules.requests, "post", return_value=Response({"DataSet":{"Rows":[{"user_exists":0}]}})):
        assert rules._check_user_id(999) is False

def test_history_returns_top_ten():
    rows = [{"product_name":str(i)} for i in range(12)]
    with patch.object(rules, "_check_user_id", return_value=True), patch.object(rules, "_post_loginom", return_value={"DataSet":{"Rows":rows}}):
        assert len(rules.get_user_history(1)) == 10

def test_missing_user():
    with patch.object(rules, "_check_user_id", return_value=False):
        with pytest.raises(ValueError, match="не найден"): rules.get_user_history(10)

@pytest.mark.parametrize("value", [0, -1, True, "1", 1.5])
def test_invalid_user_id(value):
    with pytest.raises(ValueError): rules.get_user_history(value)

def test_build_products_text():
    text = rules.build_products_text([{"product_name":"Bananas","department_rus":"Фрукты","aisle":"Fresh fruit","order_count":4}])
    assert "Bananas" in text and "Фрукты" in text and "покупок: 4" in text

def test_empty_products_text():
    assert rules.build_products_text([]) == "История покупок отсутствует."
