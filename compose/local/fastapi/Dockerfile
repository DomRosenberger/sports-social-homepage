ARG PYTHON_VERSION=3.10-slim-buster

# define an alias for the specfic python version used in this file.
FROM python:${PYTHON_VERSION} as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

WORKDIR /code

# Copy requirements file to workdir
COPY ./requirements.txt /code/requirements.txt

# Install all required dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code to workdir
COPY ./app /code/app
COPY ./static /code/static
COPY ./templates /code/templates

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
