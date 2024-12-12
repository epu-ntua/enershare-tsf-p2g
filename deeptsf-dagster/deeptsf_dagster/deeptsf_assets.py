import pandas as pd
import requests
import json
from io import StringIO
import matplotlib.pyplot as plt  # For plotting results
from dagster import multi_asset, AssetIn, AssetOut, MetadataValue, Output, graph_multi_asset 
import base64
from io import BytesIO
import json
import os
from urllib.parse import urlparse
from .db_assets import get_table_as_df, store_to_db
from datetime import datetime, timedelta

# Define API configurations
BASE_URL = "https://deeptsf-backend.toolbox.epu.ntua.gr"
ENDPOINT = "/serving/get_result"

def is_postgres_url(url):
    parsed_url = urlparse(url)
    return parsed_url.scheme.lower() == 'postgresql'

def is_filepath(s):
    return os.path.isabs(s) or os.path.isfile(s) or os.path.isdir(s)


def end_of_input_period_for_dtsf(start_dt_of_projection):
    #This function takes the timestamp of the starting hour of the requested forecast, which DeepTsF will need to make, as a string. For example:  '2025-12-29 05:00:00'
    #Then it outputs the timestamp as a timestamp object, of when the input period (for DeepTSF) ends. Namely the previous hour of when the forecast starts, namely '2023-12-29 04:00:00'.
    start_dt_of_projection_timestamp = datetime.strptime(start_dt_of_projection, '%Y-%m-%d %H:%M:%S')
    #projection_start_month, projection_start_day, projection_start_hour = start_dt_of_projection_timestamp.month, start_dt_of_projection_timestamp.day, start_dt_of_projection_timestamp.hour
    previous_timestamp = start_dt_of_projection_timestamp - timedelta(hours=1) 
    '''Output the exactly previous hour, only for year: 2023. For example, for forecast starting with '2026-10-28 12:00:00', output: '2023-10-28 11:00:00'
    '''
    dagster_end_of_input_period_timestamp= previous_timestamp.replace(year =2023) #set year to 2024
    #print(dagster_end_of_input_period_timestamp)
    return dagster_end_of_input_period_timestamp

### AUTHENTICATION ###

@multi_asset(
    name="get_keycloak_token",
    description="Op used to get Auth token from keycloak",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    outs={"keycloak_token": AssetOut(dagster_type=str)})
def get_keycloak_token():
    """Obtain an authentication token from Keycloak."""
    url = "https://keycloak.toolbox.epu.ntua.gr/realms/master/protocol/openid-connect/token"
    payload = (
        "client_id=deeptsf-backend&client_secret=FPLg7SP2U5pD6NmJdt5cue0NjBENdYX0"
        "&username=deeptsf_admin&password=deeptsf_admin&grant_type=password"
    )
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        print("Authentication successful.")
        return Output(response.json().get('access_token'), metadata={'token': MetadataValue.md(response.json().get('access_token'))})
    except requests.exceptions.RequestException as e:
        print(f"Authentication failed: {e}")
        return None

### DATA PREPARATION ###

@multi_asset(
    name="prepare_series_data",
    description="Op used to get Auth token from keycloak",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    outs={"input_series": AssetOut(dagster_type=dict)})
async def prepare_series_data(context):
    """Prepare time series data for the last 'hours' hours (default is 7 days)."""

    config = context.resources.config
    input_data_paths = config.input_data_path.split(',')

    input_series = {}
    metadata_df = pd.DataFrame()

    for input_data_path in input_data_paths:
        df = pd.DataFrame()

        if is_filepath(input_data_path):
            df = pd.read_csv(input_data_path)
        else:
            schema, table_name = input_data_path.split('.')
            df = await get_table_as_df(schema, table_name)


        input_end = end_of_input_period_for_dtsf(config.forecast_start)
        input_end = input_end.strftime(f"{input_end.year}-{input_end.month:02d}-{input_end.day:02d} {input_end.hour:02d}:{input_end.minute:02d}:{input_end.second:02d}")
        print(f"Input end: {input_end}")
    
        recent_data = df[df['Datetime']<=input_end].tail(24*7) #take the exactly preceeding 7 days of data
        print(recent_data.head(10))  # Display the first few rows
        recent_data.set_index('Datetime', inplace=True)

        # input_series = {"series": {"Value": recent_data['Value'].to_dict()}}
        input_series[input_data_path] = {"series": {"Value": recent_data['Value'].to_dict()}}

        # Add metadata for this input path
        metadata_row = recent_data['Value'].to_frame().T
        metadata_row['data_source'] = input_data_path
        metadata_df = pd.concat([metadata_df, metadata_row], ignore_index=True)

    # Reorder columns to have 'data_source' first
    cols = ['data_source'] + [col for col in metadata_df.columns if col != 'data_source']
    metadata_df = metadata_df[cols]

    return Output(input_series, metadata={'input_series': MetadataValue.md(metadata_df.to_markdown())})

### API REQUEST ###

@multi_asset(
    name="create_request_payload",
    description="Op used to construct payload for deepTSF API",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    ins={'input_series': AssetIn(key='input_series')},
    outs={"deepTSF_payload": AssetOut(dagster_type=dict)})
def create_request_payload(input_series):
    """Create the request payload with series and optional future covariates."""
    deepTSF_API_payload = {}
    run_id = None

    for input_path, series_data in input_series.items():
        if 'crete' in input_path: run_id = 'f7c4d634ebfa4500815597652d9e848e'
        elif 'wind' in input_path: run_id = '2596c1888c5b439ab52cbb5cc3a3269e'
        elif 'pv' in input_path: run_id = '18f1fc6af4cd45c1a0f837e261372719'
        else: run_id = None

        payload = {
            "run_id": run_id,
            "timesteps_ahead": 24*7,
            "series_uri": None,
            "multiple_file_type": False,
            "weather_covariates": False,
            "resolution": "1h",
            "ts_id_pred": "",
            "past_covariates": None,
            "past_covariates_uri": None,
            "future_covariates": None,
            "future_covariates_uri": None,
            "roll_size": None,
            "batch_size": None,
            "format": "long",
            "series": series_data["series"],
        }
        table_name = input_path.split('.')[1]
        deepTSF_API_payload[table_name] = payload

    formatted_payloads = json.dumps(deepTSF_API_payload, indent=5)
    markdown_preview = f"```json\n{formatted_payloads}\n```"

    return Output(deepTSF_API_payload, metadata={"request_payloads": MetadataValue.md(markdown_preview)})

@multi_asset(
    name="request_model_prediction",
    description="Op used to access deepTSF API and get prediction",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    ins={"keycloak_token": AssetIn(key='keycloak_token'), 
         "deepTSF_payload": AssetIn(key='deepTSF_payload')},
    outs={"pred_series": AssetOut(dagster_type=pd.DataFrame)})
async def request_model_prediction(context, keycloak_token, deepTSF_payload):
    """Send the request to the model prediction endpoint and return the result."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {keycloak_token}'
    }

    pred_series_combined = pd.DataFrame()
    metadata_df = pd.DataFrame()
    pred_metadata = {}

    for index, (input_path, payload) in enumerate(deepTSF_payload.items()):
        print(json.dumps(payload))
        try:
            response = requests.post(f"{BASE_URL}{ENDPOINT}", json=payload, headers=headers)
            response.raise_for_status()
            print(f"Request successful for {input_path}.")

            pred_series = pd.read_json(StringIO(response.text))
            pred_series['dataset_source'] = input_path  # Add column to signify dataset source
            pred_series['Value'] = pred_series['Value'].apply(lambda x: max(x, 0))
            print(pred_series)  # Display the first few rows

            pred_series_combined = pd.concat([pred_series_combined, pred_series], ignore_index=True)

            # Add metadata for this input path
            metadata_row = pred_series['Value'].to_frame().T
            metadata_row['data_source'] = input_path
            metadata_df = pd.concat([metadata_df, metadata_row], ignore_index=True)

            pred_series.plot(label='pred series')
            plt.title(f"{input_path}: Time series plot")
            buffer = BytesIO()
            plt.savefig(buffer, format="png"); plt.close(); 
            buffer.seek(0)  # Rewind buffer
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            # pred_metadata['pred_series'] = MetadataValue.md(str(pd.DataFrame(pred_series).transpose().to_markdown()))
            pred_metadata[f'{input_path}_plot'] = MetadataValue.md(f"![time_series_plot](data:image/png;base64,{image_data})")

            config = context.resources.config

            
            pred_series.reset_index(inplace=True)
            pred_series.rename(columns={'index': 'Datetime'}, inplace=True)
            # pred_series.set_index('Datetime', inplace=True)
            print(pred_series.head())
            current_output = config.output_data_path.split(',')[index]
            schema, table_name = current_output.split('.')
            await store_to_db(pred_series.drop(columns=['dataset_source']), table_name, schema)

            # return Output(pred_series, metadata=pred_metadata, tags={"source": config.output_data_path})
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
        except ValueError as e:
            print(f"Failed to parse response JSON: {e}")
            return None

    # Reorder columns to have 'data_source' first
    cols = ['data_source'] + [col for col in metadata_df.columns if col != 'data_source']
    metadata_df = metadata_df[cols]
    pred_metadata['pred_series_df'] = MetadataValue.md(metadata_df.to_markdown())

    return Output(pred_series_combined, metadata=pred_metadata)

### RESULTS DISPLAY ###

def display_results(result_df):
    """Display the model prediction results."""
    print("Received data:")
    
    print(result_df.head())  # Display a sample of the result
    result_df.plot()  # Plot the results if it’s a time series
    plt.show()  # Display the plot

### MAIN FUNCTION ###

@graph_multi_asset(
    name="deepTSF_pipeline",
    group_name='deepTSF_pipeline',
    outs={"keycloak_token": AssetOut(dagster_type=str),
            "input_series": AssetOut(dagster_type=dict),
            "deepTSF_payload": AssetOut(dagster_type=dict),
            "pred_series": AssetOut(dagster_type=dict)})
def deepTSF_pipeline():
    
    keycloak_token = get_keycloak_token()
    if not keycloak_token:
        print("Token acquisition failed. Exiting.")
        return
    else:
        print(f"Token Received: {keycloak_token}")
    
    # Prepare data
    input_series = prepare_series_data()

    # Build the request deepTSF_payload
    deepTSF_payload = create_request_payload(input_series)
    
    # Send request and process results
    pred_series = request_model_prediction(keycloak_token, deepTSF_payload)

    return {'keycloak_token': keycloak_token, "input_series": input_series, "pred_series": pred_series, "deepTSF_payload": deepTSF_payload} 
    