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
from .db_assets import get_table_as_df

twinP2G_API_URL = 'http://enershare1.epu.ntua.gr:9009/network_execute/'

@multi_asset(
    name="call_twinP2G_API",
    description="Op used to access twinP2G API and get prediction",
    group_name='twinp2g_pipeline',
    required_resource_keys={"config"},
    outs={"twinp2g_output": AssetOut(dagster_type=pd.DataFrame)})
async def call_twinP2G_API():

    output_metadata = {}

    try:
        response = requests.post(twinP2G_API_URL, json={"data": "string"})
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        print("Response Status Code:", response.status_code)
        print("Response Body:", response.text)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    twinp2g_output = await get_table_as_df('crete_fc_uc', 'crete_use_case_output_series')
    # pred_series_combined = pd.concat([pred_series_combined, pred_series], ignore_index=True)
    print(twinp2g_output.head())

    twinp2g_output.plot(label='twinp2g output series')
    plt.title(f"crete_use_case_output_series plot")
    buffer = BytesIO()
    plt.savefig(buffer, format="png"); plt.close(); 
    buffer.seek(0)  # Rewind buffer
    twinp2g_output_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    output_metadata[f'crete_use_case_output_series plot'] = MetadataValue.md(f"![time_series_plot](data:image/png;base64,{twinp2g_output_data})")
    output_metadata['twinp2g_output'] = MetadataValue.md(twinp2g_output.to_markdown())
    
    twinp2g_statistics = await get_table_as_df('crete_fc_uc', 'crete_use_case_statistics')
    print(twinp2g_statistics.head())

    twinp2g_statistics.plot(label='twinp2g output series')
    plt.title(f"crete_use_case_statistics_series plot")
    buffer = BytesIO()
    plt.savefig(buffer, format="png"); plt.close(); 
    buffer.seek(0)  # Rewind buffer
    twinp2g_statistics_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
    output_metadata[f'crete_use_case_statistics_series plot'] = MetadataValue.md(f"![time_series_plot](data:image/png;base64,{twinp2g_statistics_data})")
    output_metadata['twinp2g_statistics'] = MetadataValue.md(twinp2g_statistics.to_markdown())
    
    return  Output(twinp2g_output, metadata=output_metadata)

@graph_multi_asset(
    name="twinP2G_pipeline",
    group_name='twinP2G_pipeline',
    outs={"twinp2g_output": AssetOut(dagster_type=pd.DataFrame)})
def twinP2G_pipeline():

    twinp2g_output = call_twinP2G_API()

    return {"twinp2g_output": twinp2g_output}

