# Практическая работа №4 — Flask MVP с Loginom и GigaChat

**Студент:** Архангельский Данила Андреевич  
**Группа:** ИСТ-05

MVP рекомендательного сервиса Instacart: Flask принимает `user_id`, проверяет его через Loginom `CheckUserId`, получает историю через `GetUserHistory`, передаёт список товаров в GigaChat и отображает результат в HTML.

## Структура
- `app.py` — Flask-приложение и маршруты `/`, `/login`, `/logout`, `/history`, `/api/history`, `/health`.
- `business-rules.py` — три функции из задания: `get_user_history`, `build_products_text`, `ask_gigachat`.
- `templates/index.html` — интерфейс.
- `notebooks/demo_rest_api.ipynb` — предварительная проверка Loginom REST и GigaChat.
- `loginom/queries.sql`, `loginom/LOGINOM_SETUP.md` — SQL и инструкция создания сервисов.
- `tests/` — модульные тесты; `.github/workflows/tests.yml` — CI.

## Запуск
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Заполнить LOGINOM_PACKAGE и GIGA_KEY
python app.py
```
Откройте http://127.0.0.1:5000. Проверка: `/health`.

## Loginom
Исходный `instacart_ws_fio.lgp` из задания содержит SQLite-подключение и импорты `orders`, `orders_prior`, `products`, но не содержит опубликованных `GetUserHistory` и `CheckUserId`. Сама база Instacart (около 2,2 ГБ) в учебном ZIP отсутствует. Сервисы необходимо создать и опубликовать по `loginom/LOGINOM_SETUP.md`, затем установить фактическое имя пакета из `/lgi/rest/help` в `.env`.

Ожидаемый запрос: `{"Variables":{"user_id":1}}`. `GetUserHistory` должен возвращать `DataSet.Rows` с полями `product_name`, `aisle`, `department`, `department_rus`, `order_count`; `CheckUserId` — `DataSet.Rows[0].user_exists` со значением 1/0. Фактический JSON нужно сверить с учебным сервером.

## Тесты
```bash
pip install -r requirements-dev.txt
pytest -q
```
Тесты подменяют внешние API; это не интеграционный тест Loginom/GigaChat.

## Amvera
Команда запуска находится в `Procfile`: `gunicorn --bind 0.0.0.0:${PORT:-8000} app:app`. Секреты задаются в переменных окружения Amvera, `.env` не загружается. После деплоя проверьте `/health`, реальный Loginom ID-check и рекомендацию GigaChat. Остановите приложение для экономии баланса и включите перед проверкой 17.12.2026.

**Статус:** Python-проект подготовлен; Loginom-сервисы, реальные ключи, интеграционный запуск и Amvera-деплой не считаются выполненными до проверки в соответствующих внешних аккаунтах.