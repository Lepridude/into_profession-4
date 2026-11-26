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

def test_history_returns_top_ten():
    rows = [{"product_name": str(i)} for i in range(12)]
    with patch.object(rules.requests, "post", return_value=Response({"DataSet":{"Rows":rows}})):
        assert len(rules.get_user_history(1)) == 10

def test_history_sends_user_id_to_loginom():
    with patch.object(rules.requests, "post", return_value=Response({"DataSet":{"Rows":[]}})) as post:
        rules.get_user_history(25)
    assert post.call_args.kwargs["json"] == {"Variables":{"user_id":25}}

def test_invalid_user_id():
    for value in (0, -1, True, "1", 1.5):
        with pytest.raises(ValueError): rules.get_user_history(value)

def test_build_products_text():
    text = rules.build_products_text([{"product_name":"Bananas","department_rus":"Фрукты","aisle":"Fresh fruit","order_count":4}])
    assert "Bananas" in text and "Фрукты" in text and "заказов: 4" in text

def test_empty_products_text():
    assert rules.build_products_text([]) == "История покупок отсутствует."

def test_gigachat_requires_key(monkeypatch):
    monkeypatch.setattr(rules, "llm", None)
    with pytest.raises(RuntimeError, match="GIGA_KEY"):
        rules.ask_gigachat(1, "Bananas")

def test_gigachat_uses_history_context(monkeypatch):
    class Answer:
        content = "Рекомендация"
    class FakeLLM:
        def invoke(self, messages):
            assert "Bananas" in messages[1].content
            return Answer()
    monkeypatch.setattr(rules, "llm", FakeLLM())
    prompt, answer = rules.ask_gigachat(1, "Bananas")
    assert "user_id=1" in prompt and answer == "Рекомендация"
