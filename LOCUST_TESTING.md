# Нагрузочное тестирование с Locust

## Описание

Этот проект содержит настройки для нагрузочного тестирования gRPC-сервиса глоссария с помощью [Locust](https://locust.io/).

## Типы пользователей

### 1. GlossaryUser
Симулирует обычного пользователя, который выполняет различные операции:
- **GetTerm** (вес 5) - получение существующего термина
- **ListTerms** (вес 3) - получение списка терминов
- **AddTerm** (вес 1) - добавление нового термина
- **GetTerm (Not Found)** (вес 2) - запрос несуществующего термина (проверка обработки ошибок)

### 2. ReadOnlyUser
Симулирует пользователя, который только читает данные (без записи):
- **GetTerm** (вес 7)
- **ListTerms** (вес 3)

## Установка

1. Убедитесь, что gRPC сервис запущен:
```bash
docker compose up -d
```

2. Установите зависимости для тестирования:
```bash
pip install -r requirements-locust.txt
```

3. Сгенерируйте protobuf файлы (если еще не сделано):
```bash
python -m grpc_tools.protoc \
  -I./protobufs \
  --python_out=./app/generated \
  --grpc_python_out=./app/generated \
  ./protobufs/glossary.proto
```

## Запуск тестов

### Вариант 1: Web UI (рекомендуется)

Запустите Locust с веб-интерфейсом:
```bash
locust -f locustfile.py --host=localhost:50051
```

Откройте браузер по адресу: http://localhost:8089

В веб-интерфейсе укажите:
- **Number of users**: количество одновременных пользователей (например, 10)
- **Spawn rate**: скорость добавления пользователей в секунду (например, 2)
- **Host**: должен быть `localhost:50051`

### Вариант 2: Без UI (headless)

Запуск с заданными параметрами:
```bash
locust -f locustfile.py \
  --host=localhost:50051 \
  --users 10 \
  --spawn-rate 2 \
  --run-time 1m \
  --headless
```

### Вариант 3: Тестирование конкретного класса пользователей

Только читающие пользователи:
```bash
locust -f locustfile.py --host=localhost:50051 ReadOnlyUser
```

Только стандартные пользователи:
```bash
locust -f locustfile.py --host=localhost:50051 GlossaryUser
```

### Вариант 4: Комбинированная нагрузка

Запустите с разными типами пользователей одновременно:
```bash
locust -f locustfile.py \
  --host=localhost:50051 \
  --users 20 \
  --spawn-rate 2 \
  --run-time 2m \
  --headless \
  GlossaryUser ReadOnlyUser
```

## Параметры командной строки

- `--host` - адрес gRPC сервера (например, `localhost:50051`)
- `--users` или `-u` - общее количество пользователей для симуляции
- `--spawn-rate` или `-r` - скорость появления новых пользователей в секунду
- `--run-time` или `-t` - длительность теста (например, `1m`, `30s`, `1h`)
- `--headless` - запуск без веб-интерфейса
- `--csv` - сохранение результатов в CSV файлы (например, `--csv=results`)
- `--html` - генерация HTML отчета (например, `--html=report.html`)

## Примеры использования

### Быстрый тест производительности
```bash
locust -f locustfile.py \
  --host=localhost:50051 \
  --users 5 \
  --spawn-rate 1 \
  --run-time 30s \
  --headless
```

### Стресс-тест с генерацией отчета
```bash
locust -f locustfile.py \
  --host=localhost:50051 \
  --users 50 \
  --spawn-rate 5 \
  --run-time 5m \
  --headless \
  --html=stress_test_report.html \
  --csv=stress_test_results
```

### Длительный тест стабильности
```bash
locust -f locustfile.py \
  --host=localhost:50051 \
  --users 20 \
  --spawn-rate 2 \
  --run-time 30m \
  --headless \
  --html=stability_test_report.html
```

## Анализ результатов

После выполнения тестов в веб-интерфейсе или в отчетах вы увидите:

- **Statistics**: общая статистика по запросам (количество, время ответа, RPS)
- **Charts**: графики RPS, времени ответа, количества пользователей
- **Failures**: список ошибок и исключений
- **Exceptions**: детальная информация об исключениях

### Ключевые метрики

- **Total Requests per Second (RPS)** - общая пропускная способность
- **Average Response Time** - среднее время ответа
- **95th percentile** - время ответа для 95% запросов
- **Failure rate** - процент неудачных запросов

## Настройка тестов

Вы можете изменить следующие параметры в [locustfile.py](locustfile.py):

- **wait_time** - время ожидания между запросами пользователя
- **@task(вес)** - вес задачи (влияет на частоту выполнения)
- **KNOWN_KEYWORDS** - список тестовых ключевых слов
- Добавить новые типы пользователей или задачи

## Проверка работы сервиса

Перед запуском тестов убедитесь, что сервис работает:

```bash
# Проверка через grpcurl
grpcurl -plaintext localhost:50051 list

# Проверка через веб-интерфейс
open http://localhost:8080
```

## Устранение проблем

### Ошибка импорта protobuf модулей

Если возникает ошибка импорта, убедитесь, что вы сгенерировали protobuf файлы:
```bash
mkdir -p app/generated
python -m grpc_tools.protoc \
  -I./protobufs \
  --python_out=./app/generated \
  --grpc_python_out=./app/generated \
  ./protobufs/glossary.proto
```

### Сервис недоступен

Проверьте, что Docker контейнеры запущены:
```bash
docker compose ps
docker compose logs glossary-grpc
```

### Слишком много ошибок в тестах

- Уменьшите количество пользователей
- Увеличьте `wait_time` между запросами
- Проверьте логи сервиса на наличие ошибок

## Дополнительные ресурсы

- [Документация Locust](https://docs.locust.io/)
- [gRPC Python](https://grpc.io/docs/languages/python/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
