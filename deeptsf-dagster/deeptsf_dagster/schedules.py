from dagster import (
    ScheduleDefinition, 
    RunRequest, 
    ScheduleEvaluationContext, 
    schedule
)
import os
from .jobs import deeptsf_dagster_job
from .config import DeepTSFConfig

# we do this to change the current date at each run it scedules 
@schedule(job=deeptsf_dagster_job, cron_schedule="0 0 * * 1", execution_timezone='Europe/Athens') # on Monday at 00:00 GMT+3
def deeptsf_dagster_schedule(context: ScheduleEvaluationContext):

    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    
    return RunRequest(
        run_key=None,
        run_config={
            "resources": {
                "config": {
                    "config": DeepTSFConfig().to_dict()
                },
            },
        },
        tags={"date": scheduled_date},
    )

@schedule(job=deeptsf_dagster_job, cron_schedule="0 0 * * 1", execution_timezone='Europe/Athens') # on Monday at 00:00 GMT+3
def crete_schedule(context: ScheduleEvaluationContext):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")

    config = DeepTSFConfig().to_dict()
    config['input_data_path'] = 'crete_fc_uc.crete_load_long'
    config['output_data_path'] = 'crete_fc_uc.crete_load_projection'

    return RunRequest(
        run_key=None,
        run_config={
            "resources": {
                "config": {
                    "config": config
                },
            },
        },
        tags={"date": scheduled_date},
    )

@schedule(job=deeptsf_dagster_job, cron_schedule="0 0 * * 2", execution_timezone='Europe/Athens')  # Tuesday at 00:00 GMT+3
def wind_schedule(context: ScheduleEvaluationContext):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")

    # Base configuration modified for Wind
    config = DeepTSFConfig().to_dict()
    config['input_data_path'] = 'wind_cf_long'
    config['output_data_path'] = 'wind_cf_projection'

    return RunRequest(
        run_key=None,
        run_config={
            "resources": {
                "config": {
                    "config": config
                },
            },
        },
        tags={"date": scheduled_date},
    )

@schedule(job=deeptsf_dagster_job, cron_schedule="0 0 * * 1", execution_timezone='Europe/Athens')  # Wednesday at 00:00 GMT+3
def pv_schedule(context: ScheduleEvaluationContext):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")

    # Base configuration modified for PV
    config = DeepTSFConfig().to_dict()
    config['input_data_path'] = 'pv_cf_long'
    config['output_data_path'] = 'pv_cf_projection'

    return RunRequest(
        run_key=None,
        run_config={
            "resources": {
                "config": {
                    "config": config
                },
            },
        },
        tags={"date": scheduled_date},
    )