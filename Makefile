.PHONY: infra dev test unittest

infra:
	bash scripts/infra.sh

configure:
	bash scripts/configure.sh

run:
	bash scripts/run.sh

k3d:
	bash scripts/k3d.sh

destroy-k3d:
	bash scripts/destroy-k3d.sh

test:
	bash scripts/configure.sh --non-interactive

unittest:
	pytest -v -m "unittest"
