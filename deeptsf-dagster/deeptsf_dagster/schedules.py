from dagster import (
    ScheduleDefinition, 
    RunRequest, 
    ScheduleEvaluationContext, 
    schedule
)
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