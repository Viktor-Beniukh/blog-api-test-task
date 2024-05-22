FROM python:3.11 as requirements-stage

WORKDIR /tmp


RUN pip install poetry


COPY ./pyproject.toml ./poetry.lock* /tmp/


RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.11-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y netcat


WORKDIR /code


COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /code/


RUN mkdir -p /vol/web/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    fastapi-user

RUN chown -R fastapi-user:fastapi-user /vol/
RUN chmod -R 755 /vol/web/

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

USER fastapi-user

ENTRYPOINT ["/entrypoint.sh"]
