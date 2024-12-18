from dagster import define_asset_job
from .deeptsf_assets import deepTSF_pipeline
from .twinp2g_assets import twinP2G_pipeline

deeptsf_dagster_job = define_asset_job("deeptsf_dagster_job", selection=[deepTSF_pipeline])

twinP2G_dagster_job = define_asset_job("twinP2G_dagster_job", selection=[twinP2G_pipeline])

deeptsf_twinP2G_dagster_job = define_asset_job("deeptsf_twinP2G_dagster_job", selection=[deepTSF_pipeline, twinP2G_pipeline])
