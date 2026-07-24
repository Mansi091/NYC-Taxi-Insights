FROM python:3.12-slim


WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN pip install uv

COPY pyproject.toml uv.lock ./



COPY . /app

ENV MAGE_REPO_PATH=/app/data_pipeline
ENV PYTHONPATH=/app

EXPOSE 6789

CMD ["mage", "start", "data_pipeline"]
