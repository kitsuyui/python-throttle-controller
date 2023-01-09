.PHONY: lint
lint: flake8 mypy check_import_order check_format

.PHONY: test
test: pytest

.PHONY: format
format: isort black pyupgrade

.PHONY: isort
isort:
	isort throttle_controller tests

.PHONY: black
black:
	black throttle_controller tests

.PHONY: flake8
flake8:
	flake8 throttle_controller tests

.PHONY: pyupgrade
pyupgrade:
	pyupgrade --py37-plus throttle_controller/*.py throttle_controller/*.pyi tests/*.py

.PHONY: mypy
mypy:
	mypy throttle_controller tests

.PHONY: check_import_order
check_import_order:
	isort --check-only --diff throttle_controller tests

.PHONY: check_format
check_format:
	black --check throttle_controller tests

.PHONY: pytest
pytest:
	pytest --cov=throttle_controller tests --doctest-modules --cov-report=xml

.PHONY: build
build:
	python3 -m build .

.PHONY: clean
clean:
	rm -rf throttle_controller.egg-info dist
