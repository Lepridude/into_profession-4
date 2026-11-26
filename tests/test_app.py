import app

class FakeRules:
    @staticmethod
    def get_user_history(user_id): return [{"product_name":"Bananas","aisle":"Fresh fruit","department_rus":"Фрукты","order_count":4}]
    @staticmethod
    def build_products_text(rows): return "1. Bananas"
    @staticmethod
    def ask_gigachat(user_id, products_text): return "Prompt", "Рекомендация"

class CheckResponse:
    def __init__(self, exists=1): self.exists = exists
    def raise_for_status(self): pass
    def json(self): return {"DataSet":{"Rows":[{"user_exists":self.exists}]}}

def client(monkeypatch, exists=1):
    app.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    monkeypatch.setattr(app, "load_business_rules", lambda: FakeRules)
    monkeypatch.setattr(app.requests, "post", lambda *args, **kwargs: CheckResponse(exists))
    return app.app.test_client()

def test_health(monkeypatch):
    response = client(monkeypatch).get("/health")
    assert response.status_code == 200 and response.json["status"] == "ok"

def test_login_and_history(monkeypatch):
    c = client(monkeypatch)
    assert c.post("/login", data={"user_id":"1"}).status_code == 200
    response = c.post("/history")
    assert response.status_code == 200
    assert "Bananas" in response.get_data(as_text=True)
    assert "Рекомендация" in response.get_data(as_text=True)

def test_history_requires_login(monkeypatch):
    assert client(monkeypatch).post("/history").status_code == 403

def test_login_rejects_nonexistent_user(monkeypatch):
    assert client(monkeypatch, exists=0).post("/login", data={"user_id":"2"}).status_code == 404
