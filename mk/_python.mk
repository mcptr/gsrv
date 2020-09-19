PY_REQUIREMENTS_FILE 			?= requirements.txt
PY_REQUIREMENTS_DEV_FILE 		?= requirements-dev.txt


py-assert-venv:
	stat "$(VIRTUAL_ENV)" > /dev/null

py-setup: py-assert-venv
	pip install --upgrade pip
	test -f $(PY_REQUIREMENTS_FILE) && \
		pip install --upgrade -r $(PY_REQUIREMENTS_FILE)

py-setup-dev: py-assert-venv
	test -f $(PY_REQUIREMENTS_DEV_FILE) && \
		pip install --upgrade -r $(PY_REQUIREMENTS_DEV_FILE)

py-setup-all: py-setup py-setup-dev

py-clean:
	find . -type d -name __pycache__ | xargs rm -rfv
