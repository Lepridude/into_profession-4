import app

class FakeRules:
    @staticmethod
    def _check_user_id(user_id): return user_id == 1
    @staticmethod
    def get_user_history(user_id): return [{"product_name":"Bananas","aisle":"Fresh fruit","department_rus":"Фрукты","order_count":4}]
    @staticmethod
    def build_products_text(rows): return "1. Bananas"
    @staticmethod
    def ask_gigachat(user_id, products_text): return "Prompt", "Рекомендация"

def client(monkeypatch):
    app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    monkeypatch.setattr(app, "load_business_rules", lambda: FakeRules)
    return app.app.test_client()

def test_health(monkeypatch):
    response = client(monkeypatch).get("/health")
    assert response.status_code == 200 and response.json["status"] == "ok"

def test_reject_unknown_user(monkeypatch):
    response = client(monkeypatch).post("/login", data={"user_id":"2"})
    assert response.status_code == 404

def test_login_and_history(monkeypatch):
    c = client(monkeypatch)
    assert c.post("/login", data={"user_id":"1"}).status_code == 200
    response = c.post("/history")
    assert response.status_code == 200
    assert "Bananas" in response.get_data(as_text=True)
    assert "Рекомендация" in response.get_data(as_text=True)

def test_history_requires_login(monkeypatch):
    assert client(monkeypatch).post("/history").status_code == 403
