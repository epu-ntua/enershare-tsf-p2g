import pandas as pd
import requests
import json
from io import StringIO
import matplotlib.pyplot as plt  # For plotting results
from dagster import multi_asset, AssetIn, AssetOut, MetadataValue, Output, graph_multi_asset 
import base64
from io import BytesIO
import json

# Define API configurations
BASE_URL = "https://deeptsf-backend.toolbox.epu.ntua.gr"
ENDPOINT = "/serving/get_result"
CSV_FILE_PATH = "./wind.csv"

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
def prepare_series_data(context):
    """Prepare time series data for the last 'hours' hours (default is 7 days)."""

    config = context.resources.config

    df = pd.read_csv(config.csv_file_path)
    df.set_index('Datetime', inplace=True)
    df.sort_index(inplace=True)
    
    # Get data for the specified hours
    recent_data = df.tail(config.timesteps_ahead)
    
    # Format data as required by the API
    input_series = {"series": {"Value": recent_data['Value'].to_dict()}}
    
    return Output(input_series, metadata={'input_series': MetadataValue.md(str(pd.DataFrame(input_series).transpose().to_markdown()))})

### API REQUEST ###

@multi_asset(
    name="create_request_payload",
    description="Op used to construct payload for deepTSF API",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    ins={'input_series': AssetIn(key='input_series')},
    outs={"deepTSF_API_payload": AssetOut(dagster_type=dict)})
def create_request_payload(input_series):
    """Create the request payload with series and optional future covariates."""
    deepTSF_API_payload = {
        "run_id": "cf1b37db204c49f2b46a908cb98d6692",
        "timesteps_ahead": 100,
        "series_uri": None,
        "multiple_file_type": False,
        "weather_covariates": False,
        "resolution": "1h",
        "ts_id_pred": "1",
        "past_covariates": None,
        "past_covariates_uri": None,
        "future_covariates": None,
        "future_covariates_uri": None,
        "roll_size": None,
        "batch_size": None,
        "format": "long",
        "series": input_series["series"],
    }

    return Output(deepTSF_API_payload, metadata={"request_payload": json.dumps(deepTSF_API_payload, indent=2)})


@multi_asset(
    name="request_model_prediction",
    description="Op used to access deepTSF API and get prediction",
    group_name='deepTSF_pipeline',
    required_resource_keys={"config"},
    ins={"keycloak_token": AssetIn(key='keycloak_token'), 
         "deepTSF_payload": AssetIn(key='deepTSF_payload')},
    outs={"pred_series": AssetOut(dagster_type=pd.DataFrame)})
def request_model_prediction(keycloak_token, deepTSF_payload):
    """Send the request to the model prediction endpoint and return the result."""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {keycloak_token}'
    }

    try:
        response = requests.post(f"{BASE_URL}{ENDPOINT}", json=deepTSF_payload, headers=headers)
        response.raise_for_status()
        print("Request successful.")

        pred_series_json = pd.read_json(StringIO(response.text))
   
        pred_series = pred_series_json.head()
        pred_series.plot(label='pred series')
        plt.title("Time series plot")
        buffer = BytesIO()
        plt.savefig(buffer, format="png"); plt.close(); 
        buffer.seek(0)  # Rewind buffer
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        pred_metadata = {}
        pred_metadata['pred_series'] = MetadataValue.md(str(pd.DataFrame(pred_series).transpose().to_markdown()))
        pred_metadata['time_series_plot'] = MetadataValue.md(f"![time_series_plot](data:image/png;base64,{image_data})")
    
        return Output(pred_series, metadata=pred_metadata)
   
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Failed to parse response JSON: {e}")
        return None

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

    return {'keycloak_token': keycloak_token, "input_series": input_series, "pred_series": pred_series} 
    
    # if pred_series is not None:
    #     display_results(pred_series)

# def run_deepTSF_prediction():
#     """Execute the full pipeline for data preparation, authentication, and API request."""
#     token = get_keycloak_token()
#     if not token:
#         print("Token acquisition failed. Exiting.")
#         return
#     else:
#         print(f"Token Received: {token}")
    
#     # Prepare data
#     series_data = prepare_series_data(CSV_FILE_PATH)
#     future_covariates = None

#     # Build the request payload
#     payload = create_request_payload(series_data, future_covariates)
    
#     # Send request and process results
#     result = request_model_prediction(token, payload)
#     if result is not None:
#         display_results(result)

### EXECUTION ###

# if __name__ == "__main__":
#     run_deepTSF_prediction()
