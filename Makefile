.PHONY: infra dev test unittest

infra:
	bash scripts/infra.sh

configure:
	bash scripts/configure.sh

run:
	bash scripts/run.sh

run-docker:
	bash scripts/run-docker.sh

dev:
	bash scripts/dev.sh

test:
	bash scripts/configure.sh --non-interactive

unittest:
	pytest -v -m "unittest"
