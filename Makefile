SHELL := /bin/bash
setup: venv requirements
venv:
	[[ -e ./bin/python ]] || python3.8 -m venv .	

requirements:
	source bin/activate \
	  && pip install -U pip setuptools wheel \
	  && pip install -r dev-requirements.txt \
	  && pip install -e .

test:
	source .py37/bin/activate \
	  && python -B -O -m pytest --maxfail=1 \
	      --capture=no \
	      --cov --cov-report term-missing \
		  tests/

lint:
	flake8 raft tests raft_examples
