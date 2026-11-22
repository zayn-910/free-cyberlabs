FROM python:3.12.8-slim-bookworm

LABEL org.opencontainers.image.authors="zayn-910 (https://github.com/zayn-910)"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN printf '%s\n' \
      'Types: deb' \
      'URIs: https://snapshot.debian.org/archive/debian/20260712T000000Z/' \
      'Suites: bookworm' \
      'Components: main' \
      'Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg' \
      'Check-Valid-Until: no' \
      > /etc/apt/sources.list.d/debian.sources \
    && rm -f /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends openssl=3.0.20-1~deb12u2 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 clinic \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin clinic \
    && mkdir -p /srv /run/lab \
    && chown -R 10001:10001 /srv /run/lab

WORKDIR /srv
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=10001:10001 app ./app
COPY --chown=10001:10001 scripts ./scripts
RUN chmod 0755 /srv/scripts/entrypoint.sh /srv/scripts/seed.sh

USER 10001:10001
EXPOSE 8000 8081 8082
ENTRYPOINT ["/srv/scripts/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "10", "app.web:app"]
