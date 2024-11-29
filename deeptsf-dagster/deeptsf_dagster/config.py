from dagster import ConfigurableResource
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Construct the path to navigate three levels up (outside of dagster)
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

def define_type_parameters(type):
    if(type == 'pv'): return {'run_id': 'cf1b37db204c49f2b46a908cb98d6692', 'timesteps_ahead': 90}
    elif(type == 'crete'): return {'run_id': 'f7c4d634ebfa4500815597652d9e848e', 'timesteps_ahead': 168}
    elif(type == 'wind'): return {'run_id': '89aea0983dd64585b0fe87b53e6e8b02', 'timesteps_ahead': 168}

type_config = define_type_parameters(os.environ.get('TYPE'))

class DeepTSFConfig(ConfigurableResource):
    run_id: str = type_config['run_id']
    timesteps_ahead: int = type_config['timesteps_ahead']
    input_data_path: str = 'crete_fc_uc.crete_load_long' # f"{root_dir}/datasets/{os.environ.get('CSV_FILE_PATH')}"
    output_data_path: str = 'crete_fc_uc.crete_load_projection'
    csv_future_covs: str = os.environ.get('CSV_FUTURE_COVS')
    
    def to_dict(self):
        return {
            "run_id": self.run_id,
            # "timesteps_ahead": self.timesteps_ahead,
            "csv_file_path": self.input_data_path,
            "csv_future_covs": self.csv_future_covs
        }
        