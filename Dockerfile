FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY .env .

COPY . .
COPY entrypoint.sh /usr/local/bin/ 
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN python manage.py collectstatic --noinput

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["gunicorn", "pdv_project.wsgi:application", "--bind", "0.0.0.0:8000"]