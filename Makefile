PYTHON ?= python3

.PHONY: all render posts index

all: render index

render:
	$(PYTHON) scripts/render_test_design_posts.py

index:
	$(PYTHON) scripts/render_test_design_index.py

posts: render
