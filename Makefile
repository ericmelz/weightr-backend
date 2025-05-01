.PHONY: infra dev test unittest

infra:
	bash scripts/infra.sh

configure:
	bash scripts/configure.sh

run:
	bash scripts/run.sh

dev:
	bash scripts/dev.sh

test:
	pytest -v

unittest:
	pytest -v -m "unittest"
