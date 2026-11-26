"""Бизнес-логика MVP: Loginom REST API и GigaChat."""
from __future__ import annotations
import os
from typing import Any
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

load_dotenv()
LOGINOM_URL = os.getenv("LOGINOM_URL", "https://edu.loginom.dev/lgi/rest/REPLACE_WITH_PACKAGE/GetUserHistory")
GIGA_KEY = os.getenv("GIGA_KEY", "")
GIGA_MODEL = os.getenv("GIGA_MODEL", "GigaChat-2")
LOGINOM_TIMEOUT = int(os.getenv("LOGINOM_TIMEOUT", "45"))
llm = GigaChat(credentials=GIGA_KEY, model=GIGA_MODEL, verify_ssl_certs=False,
               temperature=0.3, max_tokens=500) if GIGA_KEY else None

def get_user_history(user_id: int) -> list[dict[str, Any]]:
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id должен быть положительным целым числом")
    try:
        response = requests.post(LOGINOM_URL, json={"Variables": {"user_id": user_id}}, timeout=LOGINOM_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Ошибка вызова Loginom GetUserHistory: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Loginom вернул некорректный JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Неожиданный формат ответа Loginom: ожидался JSON-объект")
    rows = payload.get("DataSet", {}).get("Rows", [])
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("Loginom: DataSet.Rows должен быть списком объектов")
    return rows[:10]

def build_products_text(rows: list[dict[str, Any]]) -> str:
    lines = []
    for i, row in enumerate(rows[:10], start=1):
        lines.append(
            f"{i}. {row.get('product_name', 'Неизвестный товар')} — "
            f"отдел: {row.get('department_rus', row.get('department', 'не указан'))}, "
            f"категория: {row.get('aisle', 'не указана')}, "
            f"заказов: {row.get('order_count', 0)}"
        )
    return "\n".join(lines) if lines else "История покупок отсутствует."

def ask_gigachat(user_id: int, products_text: str) -> tuple[str, str]:
    if llm is None:
        raise RuntimeError("Не задан GIGA_KEY. Добавьте ключ GigaChat в .env или переменные окружения.")
    system_prompt = """Ты — персональный помощник покупателя в продуктовом онлайн-магазине.
Твоя задача — анализировать историю покупок клиента и давать ему понятные,
дружелюбные рекомендации прямо в его личном кабинете.
Обращайся к клиенту на «вы», тепло и по-человечески.
Пиши кратко — не более 5–6 предложений.
Используй только факты из переданной истории покупок; не выдумывай покупки."""
    user_prompt = f"""Клиент с user_id={user_id} чаще всего покупает следующие товары:

{products_text}

Напишите клиенту короткий персональный анализ его покупок.
Начните с того, что вы заметили в его предпочтениях.
Дайте 1–2 дружеских совета — например, что стоит попробовать добавить
или на что обратить внимание. Пишите так, как будто клиент читает это
в своём личном кабинете."""
    try:
        answer = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    except Exception as exc:
        raise RuntimeError(f"Ошибка при обращении к GigaChat: {exc}") from exc
    return user_prompt, str(getattr(answer, "content", answer)).strip()
