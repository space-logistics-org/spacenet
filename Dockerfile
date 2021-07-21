FROM python:3

WORKDIR /usr/src/app

ENV ADMIN_EMAIL = ""
ENV ADMIN_PASSWORD = ""
ENV AUTH_SECRET = ""

COPY spacenet spacenet
RUN python3 -m pip install spacenet/ --use-feature=in-tree-build

COPY app app
RUN python3 -m pip install app/ --use-feature=in-tree-build

CMD ["python3", "-m", "app.provide_secrets", "${ADMIN_EMAIL}", "${ADMIN_PASSWORD}", "${AUTH_SECRET}", ";",
    "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
