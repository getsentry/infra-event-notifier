VENV_PATH = .venv

.PHONY: venv
venv:
	virtualenv -ppython3 $(VENV_PATH)
	pip install -e .

.PHONY: setup-git
setup-git: venv
	pip install pre-commit==2.13.0
	pre-commit install --install-hooks


.PHONY: update-deps
update-deps: venv
# generates k8s/cli/requirements-dev.txt from k8s/cli/requirements-dev.in
	pip install --upgrade pip pip-tools
	pip-compile \
		requirements-dev.in \
		--upgrade \
		--strip-extras



.PHONY: typecheck
typecheck:
	pip install -r requirements-dev.txt -e . 
	mypy infra_event_notifier


.PHONY: test
test:
	pip install -r requirements-dev.txt -e . 
	pytest -vv ./tests
