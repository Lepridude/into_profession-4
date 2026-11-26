"""Flask MVP: user_id validation, Loginom, GigaChat, HTML and JSON API."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "local-dev-secret-change-before-deploy")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
                  MAX_CONTENT_LENGTH=1024 * 1024)
LOGINOM_CHECK_URL = os.getenv("LOGINOM_CHECK_URL", "https://edu.loginom.dev/lgi/rest/REPLACE_WITH_PACKAGE/CheckUserId")
LOGINOM_TIMEOUT = int(os.getenv("LOGINOM_TIMEOUT", "45"))

def load_business_rules():
    path = BASE_DIR / "business-rules.py"
    if not path.exists():
        raise FileNotFoundError("Не найден business-rules.py.")
    spec = importlib.util.spec_from_file_location("business_rules", path)
    if spec is None or spec.loader is None:
        raise ImportError("Не удалось загрузить business-rules.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def check_user_exists(user_id: int) -> bool:
    try:
        response = requests.post(LOGINOM_CHECK_URL, json={"Variables": {"user_id": user_id}}, timeout=LOGINOM_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Ошибка вызова Loginom CheckUserId: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("CheckUserId вернул некорректный JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("CheckUserId: ожидался JSON-объект")
    rows = payload.get("DataSet", {}).get("Rows", [])
    value = rows[0].get("user_exists") if rows and isinstance(rows[0], dict) else None
    if value is None and isinstance(payload.get("Variables"), dict):
        value = payload["Variables"].get("user_exists")
    return str(value).strip().casefold() in {"1", "true", "yes", "да"}

def page(*, user_id=None, products=None, prompt_text=None, recommendation=None, error=None, success=None):
    return render_template("index.html", user_id=user_id, products=products, prompt_text=prompt_text,
                           recommendation=recommendation, error=error, success=success)

@app.get("/")
def index():
    error = None if (BASE_DIR / "business-rules.py").exists() else "Файл business-rules.py не найден."
    return page(user_id=session.get("user_id"), error=error)

@app.post("/login")
def login():
    raw = request.form.get("user_id", "").strip()
    if not raw.isdecimal() or int(raw) <= 0:
        return page(error="user_id должен быть положительным целым числом."), 400
    user_id = int(raw)
    try:
        if not check_user_exists(user_id):
            session.clear()
            return page(error=f"Клиент с user_id={user_id} не найден в Instacart."), 404
    except Exception as exc:
        return page(error=f"Не удалось проверить клиента через Loginom: {exc}"), 502
    session.clear()
    session["user_id"] = user_id
    return page(user_id=user_id, success="Клиент найден. Можно запускать анализ.")

@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.post("/history")
def history():
    user_id = session.get("user_id")
    if not user_id:
        return page(error="Сначала авторизуйтесь по user_id."), 403
    try:
        rules = load_business_rules()
        rows = rules.get_user_history(user_id)
        if not rows:
            return page(user_id=user_id, error="Loginom вернул пустой список товаров."), 404
        products_text = rules.build_products_text(rows)
        prompt_text, recommendation = rules.ask_gigachat(user_id, products_text)
        return page(user_id=user_id, products=rows, prompt_text=prompt_text, recommendation=recommendation)
    except Exception as exc:
        app.logger.exception("History analysis failed for user_id=%s", user_id)
        return page(user_id=user_id, error=f"Ошибка: {exc}"), 502

@app.post("/api/history")
def api_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Сначала авторизуйтесь."}), 403
    try:
        rules = load_business_rules()
        rows = rules.get_user_history(user_id)
        if not rows:
            return jsonify({"error": "История покупок не найдена.", "user_id": user_id}), 404
        products_text = rules.build_products_text(rows)
        prompt_text, recommendation = rules.ask_gigachat(user_id, products_text)
        return jsonify({"user_id": user_id, "products": rows, "prompt_text": prompt_text, "recommendation": recommendation})
    except Exception as exc:
        app.logger.exception("API history failed for user_id=%s", user_id)
        return jsonify({"error": str(exc)}), 502

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "instacart-recommendation-mvp"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG", "0") == "1")
