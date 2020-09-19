.PHONY: all test
.NOTPARALLEL: clean

PROJECT_NAME		?= gsrv

USE_PYTHON		= 1

PG_CONNSTR		?= "host=localhost dbname=$(PROJECT_NAME)"
PG_URL			?= postgresql://localhost/$(PROJECT_NAME)


CMD_PY_UNITTEST		?= python -m unittest discover -fvc


all:

clean: py-clean


setup: py-setup-all


test: pep8 test-gcore test-gsrv test-gcli


test-gcore:
	$(CMD_PY_UNITTEST) gcore/tests

test-gsrv:
	$(CMD_PY_UNITTEST) gsrv/tests

test-gcli:
	$(CMD_PY_UNITTEST) gcli/tests

pep8:
	find gcore gsrv gcli -name '*.py' | xargs -n2 pycodestyle
	find gcore/tests gsrv/tests gcli/tests -name '*.py' | xargs -n2 pycodestyle

stop:
	tmux list-sessions | grep -qs $(PROJECT_NAME)-RUN && tmux kill-session -t $(PROJECT_NAME)-RUN || true

run: stop
	tmuxp load tmuxp.json

run-web:
	PG_URL=$(PG_URL) uvicorn --reload --log-level=debug web:app 

initdb:
	dropdb --if-exists $(PROJECT_NAME)
	createdb -E utf8 $(PROJECT_NAME)
	cd gsrv/sql && psql -1 $(PROJECT_NAME) < loader.sql


include mk/base.mk
