# News Digest Bot

Telegram-бот на базе **Hermes Agent**, который по запросу собирает дайджест новостей с Хабра за указанный период и тему.

## Архитектура

```
Telegram (запрос) ──► Hermes Agent ──► skill: news-digest
                           │
                           ├──► MCP: mcp-news (RSS Хабра, фильтр по теме/периоду)
                           │
                           └──► Telegram (готовая статья)
```

- **hermes** — Hermes Agent ([NousResearch](https://github.com/nousresearch/hermes-agent)): раннер агента, Telegram-шлюз, LLM-цикл
- **mcp-news** — MCP-сервер (SSE): инструменты `get_news` и `fetch_article` на базе RSS Хабра
- **hermes/skills/news-digest.md** — skill с процедурой сборки дайджеста

## Запуск

```bash
cp .env.example .env   # вписать токены
docker compose up
```

## Переменные окружения

| Переменная               | Описание                                                      |
| ------------------------ | ------------------------------------------------------------- |
| `TELEGRAM_BOT_TOKEN`     | Токен Telegram-бота ([@BotFather](https://t.me/BotFather))    |
| `TELEGRAM_ALLOWED_USERS` | Разрешённые user ID через запятую - Опционально (пусто — все) |
| `OPENROUTER_API_KEY`     | API-ключ [OpenRouter](https://openrouter.ai/keys)             |

## LLM

Используется `openai/gpt-oss-120b` через OpenRouter (бесплатный тир доступен). Модель меняется в [`hermes/config/config.yaml`](hermes/config/config.yaml).

## MCP-инструменты

### `get_news(topic, period, limit)`

Получает список новостей с Хабра за указанный период.

| Параметр | Тип    | Описание                                         |
| -------- | ------ | ------------------------------------------------ |
| `topic`  | string | Тема/ключевое слово. Пустая строка — все новости |
| `period` | string | Период: `7d`, `24h`, `3d`, `30d`                 |
| `limit`  | int    | Максимум статей (по умолчанию 7)                 |

Ответ: `[{ title, url, published_at, source, snippet }]`

### `fetch_article(url)`

Получает расширенный текст конкретной статьи.

Ответ: `{ title, text, author, published_at }`

## Пример работы

Полный прогон: [example.md](example.md)  
Скриншот: [screen.png](screen.png)

```
Пользователь: собери дайджест по теме «AI» за последнюю неделю
Бот: [статья с введением, 4-7 аннотаций с ссылками, выводом]
```

Формат периода: `7d` (7 дней), `24h` (24 часа), `30d` (месяц).
