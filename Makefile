.PHONY: all test

PROJECT_NAME		?= gsrv

USE_PYTHON		= 1

PG_CONNSTR		?= "host=localhost dbname=$(PROJECT_NAME)"
PG_URL			?= postgresql://localhost/$(PROJECT_NAME)


all:

clean: py-clean


setup: py-setup-all


test: pep8
	python -m unittest discover t -fvc

pep8:
	find gml_core gml_server gml_client t -name '*.py' | xargs -n2 pycodestyle

stop:
	tmux list-sessions | grep -qs $(PROJECT_NAME)-RUN && tmux kill-session -t $(PROJECT_NAME)-RUN || true

run: stop
	tmuxp load tmuxp.json

run-web:
	PG_URL=$(PG_URL) uvicorn --reload --log-level=debug web:app 

initdb:
	dropdb --if-exists $(PROJECT_NAME)
	createdb -E utf8 $(PROJECT_NAME)
# 	cd gml_server/sql && psql -1 $(PROJECT_NAME) < loader.sql


include mk/base.mk
