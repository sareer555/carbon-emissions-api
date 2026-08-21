FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Seed the emission factors on image build so a fresh container is
# immediately usable even before the first startup event runs.
ENV DATABASE_URL=sqlite:///./carbon_emissions.db
RUN python -m app.seed.seed_db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
