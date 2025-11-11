# gRPC-глоссарий ВКР

## Описание
Простое gRPC-приложение на Python 3.12, реализующее словарь терминов ВКР.  
Сервис хранит ключевые термины (AST, паттерны GoF, Observer, gRPC и др.), позволяет:
- получить термин по ключу,
- вывести список терминов,
- добавить новый термин.

Хранилище — SQLite (через `aiosqlite`), общение по gRPC (protobuf).

---

## Установка и запуск
```bash
git clone https://github.com/watsmanameha/grpc-glossary
cd grpc-glossary
docker compose up --build -d
```

gRPC-сервис доступен на localhost:50051
Веб-интерфейс (grpcui) доступен на http://localhost:8080

# список терминов
grpcurl -plaintext localhost:50051 glossary.GlossaryService/ListTerms

# получить термин по ключу
grpcurl -plaintext -d '{"keyword": "ast"}' localhost:50051 glossary.GlossaryService/GetTerm

# добавить термин
grpcurl -plaintext -d '{"term": {"keyword": "ai", "title": "Искусственный интеллект", "description": "Область исследований, связанная с созданием интеллектуальных систем."}}' localhost:50051 glossary.GlossaryService/AddTerm
