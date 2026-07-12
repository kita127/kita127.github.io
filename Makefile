PYTHON ?= python3
VENV_PYTHON := $(CURDIR)/.venv/bin/python3
PYTHON_RUN := $(if $(wildcard $(VENV_PYTHON)),$(VENV_PYTHON),$(PYTHON))

.PHONY: all render index posts deps

all: render index

deps:
	$(PYTHON_RUN) -m pip install markdown pygments

render: deps
	$(PYTHON_RUN) scripts/render_test_design_posts.py

index: deps
	$(PYTHON_RUN) scripts/render_test_design_index.py

posts: render
