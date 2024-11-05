from dagster import define_asset_job
from .deeptsf_assets import deepTSF_pipeline

deeptsf_dagster_job = define_asset_job("deeptsf_dagster_job", selection=[deepTSF_pipeline])
