# Практическая работа №4 — Flask MVP + Loginom + GigaChat

**Студент:** Архангельский Данила Андреевич  
**Группа:** ИСТ-05  
**Основной удалённый репозиторий:** https://github.com/Lepridude/into_profession-4  
**Платформа контроля версий:** GitHub

[![Python tests](https://github.com/Lepridude/into_profession-4/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Lepridude/into_profession-4/actions/workflows/tests.yml)

## Что делает приложение

1. Принимает `user_id` из HTML-формы.
2. Проверяет пользователя через Loginom.
3. Получает до 10 наиболее часто покупаемых товаров.
4. Формирует контекст и передаёт его в GigaChat.
5. Показывает товары и рекомендацию в HTML, а результат также доступен через JSON API.

## Структура проекта

- `app.py` — Flask-приложение, сессия, HTML- и JSON-маршруты.
- `business-rules.py` — три обязательные функции: `get_user_history`, `build_products_text`, `ask_gigachat`.
- `templates/index.html` — пользовательский интерфейс.
- `demo_rest_api.ipynb` и `notebooks/demo_rest_api.ipynb` — проверка Loginom и GigaChat.
- `loginom/queries.sql` — SQL-запросы для `GetUserHistory` и `CheckUserId`.
- `loginom/LOGINOM_SETUP.md` — настройка и публикация сервисов в Loginom.
- `tests/` и `.github/workflows/tests.yml` — тесты и CI на GitHub Actions.
- `amvera.yml`, `Procfile`, `AMVERA_DEPLOY.md` — конфигурация облачного запуска и инструкция.

## Локальный запуск

Нужен Python 3.11 или новее.

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env
python app.py
```

Откройте http://127.0.0.1:5000. Для тестов:

```bash
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
```

## Переменные окружения

Заполните локальный `.env`:

```dotenv
LOGINOM_URL=https://edu.loginom.dev/lgi/rest/instacart_ws_teacher/GetUserHistory
LOGINOM_CHECK_URL=
LOGINOM_TIMEOUT=45
GIGA_KEY=ваш_ключ_GigaChat
GIGA_MODEL=GigaChat-2
SECRET_KEY=длинная_случайная_строка
COOKIE_SECURE=0
FLASK_DEBUG=0
```

Файл `.env` исключён через `.gitignore`. Не добавляйте в GitHub ключи GigaChat, пароли, токены или реальные секреты.

## Loginom: подтверждённый контракт и ограничение

Публичный учебный метод `GetUserHistory` использует URL:

`https://edu.loginom.dev/lgi/rest/instacart_ws_teacher/GetUserHistory`

Он принимает POST с JSON `{"Variables":{"user_id":1}}` и возвращает строки в `DataSet.Rows`. Проверка для существующего ID возвращала товары, для несуществующего — пустой список.

В публичном учебном пакете отдельный метод `CheckUserId` не опубликован. Поэтому приложение и ноутбук поддерживают два режима:

- если задан `LOGINOM_CHECK_URL`, сначала вызывается отдельный `CheckUserId`;
- если URL пуст, используется резервная проверка по наличию истории в `GetUserHistory`.

Резервный вариант подтверждает наличие заказов пользователя, но формально не заменяет отдельный метод `CheckUserId`. Для полного соответствия заданию опубликуйте `CheckUserId` в своём пакете Loginom и укажите выданный сервером URL в `.env`. Инструкция и SQL находятся в `loginom/`.

Исходный `.lgp` и база Instacart не должны считаться опубликованными только потому, что SQL и инструкция находятся в репозитории. Исходный пакет не содержит готовых опубликованных модулей, а база данных объёмом около 2,2 ГБ должна быть подключена в Loginom отдельно.

## GitHub и автоматические тесты

GitHub — основной удалённый репозиторий этого проекта. Изменения сохраняются в `main`; workflow запускается при push и pull request. Последний проверенный запуск GitHub Actions завершился успешно. Тесты используют подменённые ответы API и сами по себе не доказывают доступность реального Loginom или GigaChat.

## Статус и оставшиеся внешние шаги

- [x] Flask MVP, HTML-интерфейс, сессии и JSON-маршрут.
- [x] Три требуемые функции бизнес-логики.
- [x] Публичный `GetUserHistory` проверен; резервная проверка user_id реализована.
- [x] SQL, инструкция Loginom, ноутбук, тесты и GitHub Actions подготовлены.
- [ ] Опубликовать отдельный `CheckUserId` в Loginom и указать URL.
- [ ] Проверить реальный вызов GigaChat с действующим `GIGA_KEY`.
- [ ] Создать/проверить приложение в Amvera, привязать GitHub, добавить переменные, домен и выполнить облачный запуск.

Деплой в Amvera описан в [AMVERA_DEPLOY.md](AMVERA_DEPLOY.md). Приложение должно быть доступно для проверки 17 декабря 2026 года; до этого его можно останавливать для экономии баланса.
