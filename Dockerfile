FROM python:3

WORKDIR /usr/src/app

ENV SPACENET_ADMIN_EMAIL = "admin@example.com"
ENV SPACENET_ADMIN_PASSWORD = "password"
ENV SPACENET_AUTH_SECRET = "lcapra"

COPY spacenet spacenet
RUN python3 -m pip install spacenet/ --use-feature=in-tree-build

COPY app app
RUN python3 -m pip install app/ --use-feature=in-tree-build

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
