# Тестирование микросервиса объявлений

## Описание проекта
Автоматизированные тесты для микросервиса объявлений согласно OpenAPI спецификации.

## Endpoints
- `POST /api/1/item` - Создание объявления
- `GET /api/1/item/{id}` - Получение объявления по ID
- `GET /api/1/{sellerID}/item` - Получение всех объявлений продавца
- `GET /api/1/statistic/{id}` - Получение статистики (v1)
- `GET /api/2/statistic/{id}` - Получение статистики (v2)
- `DELETE /api/2/item/{id}` - Удаление объявления

## Установка и запуск

1. **Создать виртуальное и активировать окружение**
```bash
python -m venv .venv
source .venv/bin/activate
```

2. **Установите зависимости**
```bash
pip install -r requirements.txt
```

3. **Запустить пайтесты**
```bash
pytest test_api.py
```