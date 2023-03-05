FROM python:3

WORKDIR /usr/src/app

ENV SPACENET_ADMIN_EMAIL = "sarah@email.com"
ENV SPACENET_ADMIN_PASSWORD = "password"
ENV SPACENET_AUTH_SECRET = "secret"

COPY spacenet spacenet
RUN python3 -m pip install spacenet/ --use-feature=in-tree-build

COPY app app
RUN python3 -m pip install app/ --use-feature=in-tree-build

CMD python -m uvicorn app.src.main:app --host 0.0.0.0 --port 8000
