SHELL := /bin/bash
unexport FLASK_APP

install:
	pipenv install

install-dev:
	pipenv install --dev

run:
	pipenv run gunicorn --bind 0.0.0.0:7321 wsgi:app

debug:
	pipenv run flask run

test:
	pipenv run pytest

coverage:
	pipenv run pytest --cov=date_webhook

lint:
	pipenv run black --check date_webhook
	pipenv run flake8 date_webhook

format:
	pipenv run black date_webhook
