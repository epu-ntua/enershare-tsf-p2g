build-all:
	docker build -f Dockerfile.base -t deeptsf-dagster-base:latest .
	docker build -f Dockerfile -t deeptsf_dagster:latest .

build-base:
	docker build -f Dockerfile.base -t deeptsf-dagster-base:latest .

build:
	docker build -f Dockerfile -t deeptsf_dagster:latest .
