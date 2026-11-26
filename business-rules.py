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
LOGINOM_CHECK_SERVICE = os.getenv("LOGINOM_CHECK_SERVICE", "CheckUserId")
LOGINOM_TIMEOUT = int(os.getenv("LOGINOM_TIMEOUT", "45"))
GIGA_KEY = os.getenv("GIGA_KEY", "")
GIGA_MODEL = os.getenv("GIGA_MODEL", "GigaChat-2")


def _service_url(service_name: str) -> str:
    override = os.getenv(f"LOGINOM_{service_name.upper()}_URL")
    return override.strip() if override else f"{LOGINOM_BASE_URL}/{LOGINOM_PACKAGE}/{service_name}"


def _post_loginom(service_name: str, user_id: int) -> dict[str, Any]:
    payload = {"Variables": {"user_id": int(user_id)}}
    try:
        response = requests.post(_service_url(service_name), json=payload, timeout=LOGINOM_TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"Не удалось обратиться к Loginom ({service_name}): {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("Loginom вернул ответ не в формате JSON") from exc
    if not isinstance(data, dict):
        raise RuntimeError("Неожиданный формат ответа Loginom")
    return data


def _extract_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("DataSet", {}).get("Rows", [])
    if rows is None:
        return []
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("Ожидался DataSet.Rows — список объектов с именами полей")
    return rows


def _check_user_id(user_id: int) -> bool:
    """Call the separately published CheckUserId service."""
    data = _post_loginom(LOGINOM_CHECK_SERVICE, user_id)
    rows = _extract_rows(data)
    if rows:
        for key in ("user_exists", "exists", "is_exists", "found"):
            if key in rows[0]:
                return str(rows[0][key]).strip().casefold() in {"1", "true", "yes", "да"}
    variables = data.get("Variables", {})
    if isinstance(variables, dict):
        for key in ("user_exists", "exists", "is_exists", "found"):
            if key in variables:
                return str(variables[key]).strip().casefold() in {"1", "true", "yes", "да"}
    raise RuntimeError("CheckUserId: ожидается DataSet.Rows[0].user_exists со значением 1/0")


def get_user_history(user_id: int) -> list[dict[str, Any]]:
    """Return up to ten most frequently purchased products for an existing user."""
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("user_id должен быть положительным целым числом")
    if not _check_user_id(user_id):
        raise ValueError(f"Пользователь с user_id={user_id} не найден в Instacart")
    return _extract_rows(_post_loginom(LOGINOM_HISTORY_SERVICE, user_id))[:10]


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
