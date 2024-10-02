FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install debugging tools (ping, dnsutils for nslookup, redis-tools for redis-cli)
# RUN apt-get update && apt-get install -y \
#     iputils-ping \
#     dnsutils \
#     redis-tools \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

COPY subscriber.py .
CMD ["uvicorn", "subscriber:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]