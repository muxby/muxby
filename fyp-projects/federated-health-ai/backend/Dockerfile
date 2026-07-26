FROM python:3.11-slim

WORKDIR /srv/federated-health-ai

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY fl_core fl_core
COPY backend backend
COPY scripts scripts

ENV PYTHONPATH=/srv/federated-health-ai:/srv/federated-health-ai/backend
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "backend"]
