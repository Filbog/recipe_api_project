FROM python:3.9-alpine3.13
LABEL maintainer="Filbog"

# recommended when creating Docker Imgs with Python
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./scripts /scripts
COPY ./app /app
WORKDIR /app
EXPOSE 8000

#indicates that it's dev env, so for example it installs dev requirements
ARG DEV=false
#this runs our venv
RUN python -m venv /py && \
    #this installs our requirements in the venv
    /py/bin/pip install --upgrade pip && \
    # installing dependencies for psycopg2
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev linux-headers && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    #we don't need tmp folder anymore, so we delete it to keep the docker img as lightweight as possible as possible
    rm -rf /tmp && \
    #this line deletes packages neccessary only for installing psycopg2, not running it. So we don't need them after psycopg2 is installed
    apk del .tmp-build-deps && \
    #security best practice to create a new user, not use root user
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    # Creates directories for our static and media files
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    # change owner of the directory and its subdirectories to our django-user
    chown -R django-user:django-user /vol && \
    # change permissions on that directory - 755 gives us full access and control
    chmod -R 755 /vol && \
    chmod -R +x /scripts

#this is so that we don't have to type /py/bin/python everytime we want to run python
ENV PATH="/scripts:/py/bin:$PATH"

#changes current user to django-user. This is a security best practice
USER django-user

CMD ["run.sh"]