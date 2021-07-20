FROM python:3

WORKDIR /usr/src/app

COPY spacenet spacenet
RUN python3 -m pip install spacenet/ --use-feature=in-tree-build

COPY app app
RUN python3 -m pip install app/ --use-feature=in-tree-build

RUN python3 -m app.provide_secrets $ADMIN_EMAIL $ADMIN_PASSWORD $AUTH_SECRET

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
