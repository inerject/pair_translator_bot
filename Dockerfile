FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY pair_translator_bot/ ./pair_translator_bot/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "pair_translator_bot.main"]
