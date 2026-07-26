FROM python:3.11-slim

WORKDIR /srv/federated-health-ai

COPY requirements-fl.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements-fl.txt

COPY fl_core fl_core

ENV PYTHONPATH=/srv/federated-health-ai
ENV PYTHONUNBUFFERED=1

# Overridden by docker-compose: flower_server for the aggregator,
# flower_client with --client-id N for each hospital node.
CMD ["python", "-m", "fl_core.flower_server", "--rounds", "10", "--min-clients", "2"]
