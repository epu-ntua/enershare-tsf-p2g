# enershare-tsf-p2g

A [Dagster](https://dagster.io/) project for time series forecasting and integration with the twinP2G API.

## Features

- DeepTSF pipeline for time series forecasting using external API and database sources.
- TwinP2G pipeline for retrieving and visualizing results from the twinP2G API.
- Modular asset-based design using Dagster's asset/job/schedule abstractions.
- Database integration via SQLAlchemy.
- Dockerized for easy deployment.

## Project Structure

- `deeptsf-dagster/`: Main Python package and Dagster code location.
  - `deeptsf_dagster/`: Source code (assets, jobs, schedules, config).
  - `deeptsf_dagster_tests/`: Unit tests.
- `python_requirements.txt`: Python dependencies.
- `Dockerfile`, `Dockerfile.base`, `docker-compose.yml`: Containerization and orchestration.
- `Makefile`: Build commands.

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (optional, for containerized runs)
- PostgreSQL database (for asset storage)

### Installation

```sh
pip install -e "deeptsf-dagster[dev]"
```

### Running Dagster

```sh
cd deeptsf-dagster
dagster dev
```

Visit [http://localhost:3000](http://localhost:3000) to access the Dagster UI.

### Running with Docker

```sh
make build-all
docker-compose up
```

### Running Tests

```sh
pytest deeptsf-dagster/deeptsf_dagster_tests
```

## Configuration

- Edit environment variables in a `.env` file at the project root (see [deeptsf-dagster/deeptsf_dagster/config.py](deeptsf-dagster/deeptsf_dagster/config.py) for required variables).
- Adjust database connection and asset paths as needed.

## License

Specify your license here.

---

For more details, see [deeptsf-dagster/README.md](deeptsf-dagster/README.md).
