from dagster import (
    ScheduleDefinition, 
    RunRequest, 
    ScheduleEvaluationContext, 
    schedule
)
import os
from .jobs import deeptsf_dagster_job
from .config import DeepTSFConfig
import pytz

# we do this to change the current date at each run it scedules 
@schedule(job=deeptsf_dagster_job, cron_schedule="0 * * * *", execution_timezone='Europe/Athens') # on Monday at 00:00 GMT+2
def deeptsf_dagster_schedule(context: ScheduleEvaluationContext):
    # Ensure the scheduled execution time is in the Europe/Athens timezone
    # athens_tz = pytz.timezone('Europe/Athens')
    # scheduled_date = context.scheduled_execution_time.astimezone(athens_tz).strftime('%Y-%m-%d %H:%M:%S')
    scheduled_date = context.scheduled_execution_time.strftime('%Y-%m-%d %H:%M:%S')

    config = DeepTSFConfig().to_dict()
    config['forecast_start'] = scheduled_date

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
