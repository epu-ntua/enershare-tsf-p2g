from dagster import ConfigurableResource
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime

load_dotenv()

# Construct the path to navigate three levels up (outside of dagster)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

class DeepTSFConfig(ConfigurableResource):
    # run_id: str = type_config['run_id']
    forecast_start: str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    input_data_path: str = "crete_fc_uc.crete_load_long,crete_fc_uc.wind_cf_long2,crete_fc_uc.pv_cf_long2" # f"{root_dir}/datasets/{os.environ.get('CSV_FILE_PATH')}"
    output_data_path: str = 'crete_fc_uc.crete_load_projection,crete_fc_uc.wind_cf_projection2,crete_fc_uc.pv_cf_projection2'
    csv_future_covs: str = os.environ.get('CSV_FUTURE_COVS')
    
    def to_dict(self):
        return {
            # "run_id": self.run_id,
            "forecast_start": self.forecast_start,
            "input_data_path": self.input_data_path,
            "output_data_path": self.output_data_path,
            "csv_future_covs": self.csv_future_covs
        }
        