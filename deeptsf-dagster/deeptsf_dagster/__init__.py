from dagster import Definitions
from .config import DeepTSFConfig
from .deeptsf_assets import deepTSF_pipeline
from .schedules import deeptsf_dagster_schedule
from .jobs import deeptsf_dagster_job

defs = Definitions(
    assets=[deepTSF_pipeline],
    jobs=[deeptsf_dagster_job],
    resources={
        "config": DeepTSFConfig(),
    },
    schedules=[deeptsf_dagster_schedule]
)