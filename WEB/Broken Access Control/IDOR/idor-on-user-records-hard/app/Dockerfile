# Northgate Care Network patient portal.
# Base image is pinned by digest. To refresh it after a new Python release:
#   docker buildx imagetools inspect python:3.13-slim --format '{{.Manifest.Digest}}'

FROM python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PORTAL_DATA_DIR=/data

RUN groupadd --system --gid 10001 portal \
    && useradd --system --uid 10001 --gid portal --home-dir /app --shell /usr/sbin/nologin portal \
    && mkdir -p /data \
    && chown portal:portal /data \
    && chmod 700 /data

COPY app/requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir --requirement /tmp/requirements.txt

COPY app/ /app/
COPY scripts/ /app/scripts/
RUN chmod 0755 /app/scripts/entrypoint.sh /app/scripts/seed.sh

WORKDIR /app
USER portal:portal

EXPOSE 8000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
