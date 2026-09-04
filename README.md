# Pair Translator Bot

A lightweight Telegram bot for fast translation between a fixed pair of languages.

The bot is intentionally focused on a two-language workflow rather than being a universal translator. The current direction is shown on a single persistent button and can be switched with one tap.

It supports both text and Telegram voice messages.

## Features

- Telegram bot based on aiogram 3
- Two-way translation between a fixed language pair
- Single-button translation direction switch
- Automatic direction switching for text when the input language can be identified reliably
- Voice message transcription
- Google Cloud Translation API
- Google Cloud Speech-to-Text API
- User whitelist
- Rotating application and optional message-content logs
- Docker image and Docker Compose example

## Current language pair

The current implementation is configured for:

```text
Russian ↔ Ukrainian
```

The project structure is intended to allow the fixed language pair to be generalized later without turning the bot into a universal multi-language translator.

## Requirements

- Docker with Docker Compose
- A Telegram bot token
- A Google Cloud project with billing enabled
- Cloud Translation API enabled
- Cloud Speech-to-Text API enabled
- A Google Cloud service account with access to both APIs
- A JSON service-account key

## Quick start

Clone the repository:

```bash
git clone https://github.com/inerject/pair_translator_bot.git
cd pair_translator_bot
```

Create the deployment files:

```bash
cp compose.example.yml docker-compose.yml
cp compose.env.example .env
mkdir -p credentials logs cache
```

Place your Google Cloud service-account key at:

```text
credentials/service-account.json
```

Edit `.env`:

```dotenv
PAIR_TRANSLATOR_BOT_TOKEN=123456789:YOUR_TELEGRAM_BOT_TOKEN
PAIR_TRANSLATOR_BOT_ALLOWED_USER_IDS=[123456789]
PAIR_TRANSLATOR_BOT_GOOGLE_CLOUD_PROJECT=my-google-cloud-project
```

Then start the bot:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f
```

The Compose example uses the public Docker image:

```text
inerject/pair-translator-bot:latest
```

## Google Cloud setup

Create or select a Google Cloud project and enable:

- Cloud Translation API
- Cloud Speech-to-Text API

Create a service account with access to both APIs, generate a JSON key, and save it as:

```text
credentials/service-account.json
```

The credentials directory is mounted read-only into the container.

## Telegram setup

Create a bot through `@BotFather` and put its token into `.env`.

Set the Telegram user IDs that are allowed to use the bot:

```dotenv
PAIR_TRANSLATOR_BOT_ALLOWED_USER_IDS=[123456789]
```

Multiple IDs can be specified:

```dotenv
PAIR_TRANSLATOR_BOT_ALLOWED_USER_IDS=[123456789,987654321]
```

## Configuration

Runtime configuration is read from environment variables.

Required:

```text
BOT_TOKEN
ALLOWED_USER_IDS
GOOGLE_CLOUD_PROJECT
GOOGLE_APPLICATION_CREDENTIALS
```

Optional:

```text
LOG_MESSAGE_TEXT
LOG_MAX_BYTES
LOG_BACKUP_COUNT
MESSAGE_LOG_MAX_BYTES
MESSAGE_LOG_BACKUP_COUNT
```

See `.env.example` and `compose.example.yml` for details.

`TZ` can also be set in Docker Compose if local timestamps are desired:

```yaml
environment:
  TZ: "Europe/Kyiv"
```

## Running from source

Python 3.13 or newer is required.

Install the project:

```bash
pip install -e .
```

Copy `.env.example` to `.env`, configure it, place the Google service-account key at the path specified by `GOOGLE_APPLICATION_CREDENTIALS`, then run:

```bash
python -m pair_translator_bot.main
```

## Docker image

Public image:

```text
inerject/pair-translator-bot:latest
```

The repository also contains development tooling for building and publishing the image remotely on a Linux host over SSH.

## Logging

Application logs are written to:

```text
logs/app.log
```

Message-content logging is disabled by default. When enabled with:

```dotenv
LOG_MESSAGE_TEXT=true
```

message content is written separately under:

```text
logs/messages/
```

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
