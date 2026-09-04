# Pair Translator Bot

A lightweight Telegram bot for fast translation between a fixed pair of languages.

The bot is intentionally focused on a two-language workflow rather than being a universal translator. The current direction is shown on a single persistent button and can be switched with one tap.

It supports both text and Telegram voice messages.

## Features

- Telegram bot based on aiogram 3
- Two-way translation between a configured language pair
- Single-button translation direction switch
- Automatic direction switching for text when the input language can be identified reliably
- Voice message transcription
- Google Cloud Translation API
- Google Cloud Speech-to-Text API
- User whitelist
- Persistent translated help-text cache
- Rotating application and optional message-content logs
- Docker image and Docker Compose example

## Current language pair

The current implementation is configured for:

```text
Russian ↔ Ukrainian
```

The project structure is intended to allow the fixed language pair to be generalized later without turning the bot into a universal multi-language translator.

## Requirements

For the Docker deployment:

- Docker with Docker Compose
- A Telegram bot token
- A Google Cloud project with billing enabled
- Cloud Translation API enabled
- Cloud Speech-to-Text API enabled
- A Google Cloud service account with access to both APIs
- A JSON service-account key

## Quick start with Docker Compose

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

Create a service account and grant it the required access for Translation and Speech-to-Text.

Create a JSON key for the service account and save it as:

```text
credentials/service-account.json
```

The credentials directory is mounted read-only into the container.

Do not commit the JSON key.

## Telegram setup

Create a bot through `@BotFather` and copy its bot token into `.env`.

Set the Telegram user IDs that are allowed to use the bot:

```dotenv
PAIR_TRANSLATOR_BOT_ALLOWED_USER_IDS=[123456789]
```

Multiple IDs can be specified:

```dotenv
PAIR_TRANSLATOR_BOT_ALLOWED_USER_IDS=[123456789,987654321]
```

The bot automatically registers the `/start` and `/help` commands on startup.

## Bot behavior

`/start` resets the translation direction to the default direction and displays the help text.

`/help` displays the same help text without changing the current direction.

For text messages, the bot may automatically switch the translation direction when the input language can be identified reliably.

Voice messages are recognized using the language shown before the arrow on the direction button.

Example:

```text
RU → UK
```

means that a voice message is recognized as Russian and translated into Ukrainian.

## Help-text cache

The canonical help text is stored in English in the source code.

When help is requested for the first time:

1. the bot checks the in-memory cache;
2. then the persistent file cache;
3. if no cached translation exists, Google Translation is used;
4. the translated text is saved to the cache;
5. if translation fails, the English text is used as a fallback.

The cache filename includes a hash of the English source text, so changing the source text automatically invalidates the previous translation.

The cache is stored under:

```text
/app/cache
```

and the Compose example persists it in:

```text
./cache
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

See `.env.example` and `compose.example.yml` for examples.

`TZ` can also be set in Docker Compose if local timestamps are desired:

```yaml
environment:
  TZ: "Europe/Kyiv"
```

## Running from source

Python 3.13 or newer is required. The current package dependencies are defined in `pyproject.toml`.

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then install the project:

```bash
pip install -e .
```

Copy the environment example:

```bash
cp .env.example .env
```

Configure `.env`, place the Google service-account key at the path specified by `GOOGLE_APPLICATION_CREDENTIALS`, then run:

```bash
python -m pair_translator_bot.main
```

## Docker image

Public image:

```text
inerject/pair-translator-bot:latest
```

The repository also contains tooling for building and publishing the image remotely on a Linux host over SSH.

These scripts are primarily development tooling and are not required to run the published image.

## Logging

Application logs are written to:

```text
logs/app.log
```

Message-content logging is disabled by default.

When enabled with:

```dotenv
LOG_MESSAGE_TEXT=true
```

translated message content is written separately under:

```text
logs/messages/
```

Be aware that these logs may contain private message text.

## Security notes

Never commit:

- Telegram bot tokens
- Google Cloud service-account keys
- `.env` files containing real credentials
- private message logs

The repository's `.gitignore` excludes credentials, logs, caches and local `.env` files.

## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
