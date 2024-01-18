FROM python:3.9-alpine3.13
LABEL maintainer="Filbog"

# recommended when creating Docker Imgs with Python
ENV PYTHONBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000

#indicates that it's dev env, so for example it installs dev requirements
ARG DEV=false
#this runs our venv
RUN python -m venv /py && \
    #this installs our requirements in the venv
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    #we don't need tmp folder anymore, so we delete it to keep the docker img as lightweight as possible as possible
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    #security best practice to create a new user, not use root user
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#this is so that we don't have to type /py/bin/python everytime we want to run python
ENV PATH="/py/bin:$PATH"

#changes current user to django-user. This is a security best practice
USER django-user