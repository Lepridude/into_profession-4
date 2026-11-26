"""Business logic for the Instacart recommendation MVP."""
from __future__ import annotations
import os
from typing import Any
import requests
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat

load_dotenv()
LOGINOM_BASE_URL = os.getenv("LOGINOM_BASE_URL", "https://edu.loginom.dev/lgi/rest").rstrip("/")
LOGINOM_PACKAGE = os.getenv("LOGINOM_PACKAGE", "instacart_ws_fio")
LOGINOM_HISTORY_SERVICE = os.getenv("LOGINOM_HISTORY_SERVICE", "GetUserHistory")
LOGINOM_TIMEOUT = int(os.getenv("LOGINOM_TIMEOUT", "45"))
GIGA_KEY = os.getenv("GIGA_KEY", "")
GIGA_MODEL = os.getenv("GIGA_MODEL", "GigaChat-2")


def get_user_history(user_id: int) -> list[dict[str, Any]]:
    """Return up to ten most frequently purchased products for a client."""
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id должен быть положительным целым числом")
    service_url = os.getenv("LOGINOM_GETHISTORY_URL") or (
        f"{LOGINOM_BASE_URL}/{LOGINOM_PACKAGE}/{LOGINOM_HISTORY_SERVICE}"
    )
    try:
        response = requests.post(service_url, json={"Variables": {"user_id": user_id}},
                                 timeout=LOGINOM_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Не удалось обратиться к Loginom ({LOGINOM_HISTORY_SERVICE}): {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Loginom вернул ответ не в формате JSON") from exc
    rows = data.get("DataSet", {}).get("Rows", []) if isinstance(data, dict) else []
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("Ожидался DataSet.Rows — список объектов с именами полей")
    return rows[:10]


def build_products_text(rows: list[dict[str, Any]]) -> str:
    """Format product rows as compact prompt context."""
    if not rows:
        return "История покупок отсутствует."
    lines = []
    for i, row in enumerate(rows[:10], start=1):
        name = row.get("product_name") or "Неизвестный товар"
        department = row.get("department_rus") or row.get("department") or "не указан"
        aisle = row.get("aisle") or "не указана"
        count = row.get("order_count", 0)
        lines.append(f"{i}. {name} — отдел: {department}, категория: {aisle}, покупок: {count}")
    return "\n".join(lines)


def ask_gigachat(user_id: int, products_text: str) -> tuple[str, str]:
    """Generate a short recommendation grounded in the supplied purchase history."""
    if not GIGA_KEY:
        raise RuntimeError("Не задан GIGA_KEY. Добавьте ключ GigaChat в .env.")
    system_prompt = (
        "Ты — персональный помощник покупателя продуктового онлайн-магазина. "
        "Анализируй только переданную историю покупок. Не утверждай, что клиент покупал "
        "товары, которых нет в списке. Не делай медицинских выводов и не приписывай "
        "клиенту личные качества. Обращайся на «вы». Дай краткий анализ и 1–2 совета, "
        "не более 5–6 предложений."
    )
    user_prompt = (
        f"Клиент: user_id={user_id}.\n\nИстория наиболее частых покупок:\n"
        f"{products_text}\n\nСоставь короткий персональный анализ. Отделяй наблюдения "
        "из списка от предположений и не выдумывай факты."
    )
    try:
        llm = GigaChat(credentials=GIGA_KEY, model=GIGA_MODEL, verify_ssl_certs=False,
                       temperature=0.3, max_tokens=500)
        answer = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
    except Exception as exc:
        raise RuntimeError(f"Ошибка при обращении к GigaChat: {exc}") from exc
    return user_prompt, str(getattr(answer, "content", answer)).strip()
