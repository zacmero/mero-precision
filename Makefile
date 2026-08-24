PYTHON ?= python3
EXPERIMENT ?= pilot-001
TASKS ?= 12
REPLICATES ?= 1
SEED ?= 20260824

.PHONY: check test validate benchmark-example benchmark-init

check: test validate benchmark-example

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

validate:
	$(PYTHON) scripts/validate_repo.py
	node --experimental-strip-types --check extensions/pi/index.ts
	bash -n scripts/publish_github.sh

benchmark-example:
	$(PYTHON) benchmark/scripts/validate.py benchmark/examples/run-records.jsonl \
		--manifest benchmark/examples/task-manifest.json \
		--artifact-root benchmark/examples \
		--require-complete \
		--require-artifacts
	$(PYTHON) benchmark/scripts/analyze.py benchmark/examples/run-records.jsonl \
		--manifest benchmark/examples/task-manifest.json \
		--output /tmp/mero-precision-example-report.md

benchmark-init:
	$(PYTHON) benchmark/scripts/init_experiment.py \
		benchmark/experiments/$(EXPERIMENT) \
		--experiment-id $(EXPERIMENT) \
		--tasks $(TASKS) \
		--replicates $(REPLICATES) \
		--seed $(SEED)
