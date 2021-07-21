FROM python:3

WORKDIR /usr/src/app

ENV ADMIN_EMAIL = ""
ENV ADMIN_PASSWORD = ""
ENV AUTH_SECRET = ""

COPY spacenet spacenet
RUN python3 -m pip install spacenet/ --use-feature=in-tree-build

COPY app app
RUN python3 -m pip install app/ --use-feature=in-tree-build

COPY app/start.sh scripts/start.sh
RUN ["chmod", "+x", "scripts/start.sh"]
ENTRYPOINT ["scripts/start.sh"]
