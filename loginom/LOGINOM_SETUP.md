# Loginom: настройка двух веб-сервисов

Исходный `instacart_ws_fio.lgp` создан в Loginom 7.3.1. Он содержит SQLite-подключение `Instacart` и импорты `orders`, `orders_prior`, `products`. Путь базы в исходном пакете относительный: `data/instacart_db.sqlite`; сама БД (~2,2 ГБ) в архив не вложена. В исходном пакете пока нет `GetUserHistory` и `CheckUserId`.

## Подготовка
1. Откройте исходный LGP в Loginom 7.3.1+ и сохраните копию `АрхангельскийДанила_Instacart.lgp`.
2. Перенастройте подключение `Instacart` на фактический файл `instacart_db.sqlite`.
3. Убедитесь, что импорты `orders`, `orders_prior`, `products` выполняются без ошибки.

## GetUserHistory
Создайте модуль `GetUserHistory`, входную переменную `user_id` типа Integer и узел «База данных». Используйте первый SQL из `queries.sql`, связав `:user_id` с входной переменной. Выходная таблица должна иметь поля `product_name`, `aisle`, `department`, `department_rus`, `order_count`. Опубликуйте модуль с именем `GetUserHistory`.

## CheckUserId
Создайте второй модуль `CheckUserId` с входной переменной `user_id` типа Integer. Используйте второй SQL из `queries.sql`. Выход — одна строка с полем `user_exists` (1 — найден, 0 — не найден). Опубликуйте модуль с именем `CheckUserId`.

## Публикация
1. Перенесите пакет на https://edu.loginom.dev/app/ и укажите путь к базе, доступный серверу.
2. В разделе «Веб-сервисы» опубликуйте пакет с генерацией уникального имени.
3. Откройте https://edu.loginom.dev/lgi/rest/help и скопируйте фактический URL/имя пакета в `LOGINOM_PACKAGE` файла `.env`.
4. Проверьте POST обоих методов. Ожидаемое тело: `{"Variables":{"user_id":1}}`.

## Контракт Python
`GetUserHistory` должен вернуть `DataSet.Rows` — список объектов с названными полями. `CheckUserId` должен вернуть `DataSet.Rows[0].user_exists` со значением 1/0. Сверьте фактический JSON на учебном сервере: если формат отличается, адаптируйте парсер в `business-rules.py`.

**Проверка схемы:** методичка не содержит DDL базы. Проверьте фактическое имя русифицированного поля отдела (`department_rus`) и параметры SQL в вашем Loginom перед публикацией.
