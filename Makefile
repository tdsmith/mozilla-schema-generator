.PHONY: help clean clean-pyc clean-build list test coverage release

help:
	@echo "  clean-build - remove build artifacts"
	@echo "  clean-pyc - remove Python file artifacts"
	@echo "  lint - check style with flake8"
	@echo "  test - run tests quickly with the default Python"
	@echo "  coverage - check code coverage quickly"
	@echo "  coverage-report - open the coverage report in your browser"
	@echo "  release - package and upload a release"
	@echo "  install-requirements - install the requirements for development"
	@echo "  build       Builds the docker images for the docker-compose setup"
	@echo "  clean       Stops and removes all docker containers"
	@echo "  run         Run a command. Can run scripts, e.g. make run COMMAND=\"./scripts/schema_generator.sh\""
	@echo "  test-script Run a local script. e.g. make test-script SCRIPT=\"a-local-script.sh\""
	@echo "  shell       Opens a Bash shell"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 mozilla_schema_generator tests --max-line-length 100

test:
	py.test

coverage:
	pytest tests/ --cov=mozilla_schema_generator
	coverage report -m

coverage-report: coverage
	coverage html
	open htmlcov/index.html

release: dist
	twine upload dist/*

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install-requirements:
	pip install -r requirements/requirements.txt
	pip install -r requirements/test_requirements.txt

build:
	docker-compose build

clean: stop
	docker-compose rm -f

shell:
	docker-compose run app bash

run:
	docker-compose run app $(COMMAND)

run-script:
	docker-compose run app bash < $(SCRIPT)

stop:
	docker-compose down
	docker-compose stop

up:
	docker-compose up
