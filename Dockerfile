FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml ./
COPY ru_uk_bot/ ./ru_uk_bot/

RUN pip install --no-cache-dir .

CMD ["python", "-m", "ru_uk_bot.main"]
