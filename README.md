# Практическая работа №4 — Flask MVP + Loginom + GigaChat

**Студент:** Архангельский Данила Андреевич  
**Группа:** ИСТ-05  
**Репозиторий:** https://github.com/Lepridude/into_profession-4

## Состав проекта
- `app.py` — Flask: проверка `user_id` через `CheckUserId`, сессии, HTML- и JSON-маршруты.
- `business-rules.py` — ровно три функции задания: `get_user_history`, `build_products_text`, `ask_gigachat`.
- `templates/index.html` — интерфейс.
- `demo_rest_api.ipynb` — ноутбук в корне; копия также в `notebooks/`.
- Исходный `instacart_ws_fio.lgp` из материалов занятия включён в подготовленный ZIP-архив проекта (в GitHub хранится SQL и инструкция).
- `loginom/queries.sql`, `loginom/LOGINOM_SETUP.md` — запросы и инструкция двух Loginom-сервисов.
- `tests/`, `.github/workflows/tests.yml` — автоматические тесты и CI.
- `reflection4.md` — рефлексия.
- `Procfile`, `AMVERA_DEPLOY.md` — подготовка к облачному запуску.

## Локальный запуск
Python 3.11 рекомендуется.

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
```

Заполните `.env` полными URL, которые Loginom покажет после публикации:
```dotenv
LOGINOM_URL=https://edu.loginom.dev/lgi/rest/УНИКАЛЬНОЕ_ИМЯ/GetUserHistory
LOGINOM_CHECK_URL=https://edu.loginom.dev/lgi/rest/УНИКАЛЬНОЕ_ИМЯ/CheckUserId
GIGA_KEY=ваш_ключ
```

Затем запустите `python app.py` и откройте http://127.0.0.1:5000. Health check: `/health`.

## Контракт Loginom
`CheckUserId` возвращает `DataSet.Rows[0].user_exists` (1/0). `GetUserHistory` возвращает `DataSet.Rows` с `product_name`, `department_rus`, `aisle`, `order_count`. Фактическое уникальное имя пакета генерируется сервером при публикации — его нельзя достоверно угадать заранее.

Исходный LGP из занятия содержит SQLite-подключение и импорты `orders`, `orders_prior`, `products`, но сами методы ещё не созданы. База Instacart (~2,2 ГБ) в архив не вложена. Для создания/публикации методов нужны база и доступ к серверу Loginom РЭУ; см. `loginom/LOGINOM_SETUP.md`.

## Тесты
```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```
Тесты используют mock-ответы API и не подтверждают сетевую доступность Loginom/GigaChat.

## Amvera
`amvera.yml` задаёт Python 3.11, запуск Gunicorn на `0.0.0.0:8000` и `containerPort: 8000`. В панели Amvera загрузите проект без `.env` как обычного файла, импортируйте его значения в «Переменные и секреты», соберите и запустите приложение. Проверьте `/health`, авторизацию и анализ. После проверки остановите приложение для экономии баланса; включите перед проверкой 17.12.2026.

## Текущий статус
Кодовая часть подготовлена. Реальная интеграция требует опубликованных Loginom-сервисов, доступной серверу базы Instacart и живой проверки GigaChat. Развёртывание требует доступа к аккаунту Amvera. Эти внешние этапы не отмечены как завершённые.
