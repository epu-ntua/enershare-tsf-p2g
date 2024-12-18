from dagster import Definitions
from .config import DeepTSFConfig
from .deeptsf_assets import deepTSF_pipeline
from .schedules import deeptsf_dagster_schedule 
from .jobs import deeptsf_dagster_job, twinP2G_dagster_job, deeptsf_twinP2G_dagster_job
from .twinp2g_assets import twinP2G_pipeline

defs = Definitions(
    assets=[deepTSF_pipeline, twinP2G_pipeline],
    jobs=[deeptsf_dagster_job, twinP2G_dagster_job, deeptsf_twinP2G_dagster_job],
    resources={
        "config": DeepTSFConfig(),
    },
    schedules=[deeptsf_dagster_schedule],
)