import json
import pandas as pd
from sqlalchemy import create_engine, MetaData, text, Table, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.sql import func
from contextlib import contextmanager
from dotenv import load_dotenv
import os

# Load variables from .env file
# Get the current directory
current_dir = os.path.dirname(__file__)

# Set the path to the .env file in the parent directory
# env_path = os.path.join(os.path.dirname(current_dir), '.env')

# Load the .env file
load_dotenv(current_dir)

# Access environmental variables
database_url = os.environ.get('DATABASE_URL')

# Create engine with database URL
engine = create_engine(database_url, pool_pre_ping=True)

# Create an inspector
inspector = inspect(engine)

@contextmanager
def get_db_session():
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()

# Function to check if a table exists in a specific schema
def table_exists_in_schema(table_name, schema_name):
    try:
        # Get list of table names in the specified schema
        tables = inspector.get_table_names(schema=schema_name)
        # Check if the specified table is in the list
        return table_name in tables
    except Exception as e:
        print(f"Error checking if table exists: {e}")
        return False
    
# Create a dependency to get the database metadata
def get_metadata(schema='public'):
    metadata = MetaData()
    metadata.reflect(bind=engine, schema=schema)    
    return metadata

# Function to create schema
async def create_schema(schema_name):
    try:
        with engine.connect() as connection:
            if engine.dialect.has_schema(connection, schema_name):
                print(f"Schema \"{schema_name}\" succesfully created")
            else:
                connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS {schema_name};'))
                # connection.execute(CreateSchema(schema_name, if_not_exists=True))                
                connection.commit()
                print(f"Schema \"{schema_name}\" succesfully created")
    except Exception as e:
        print("An error occurred while creating scheama in the database:", e)

async def store_to_db(data, table_name, schema_name):
    try:
        # if table_exists_in_schema(table_name, schema_name):
        #     data.to_sql(table_name, engine, schema=schema_name, if_exists='append', index=False)
        #     print("Data has been successfully stored in the database at an existing table.")
        # else:
        await create_schema(schema_name.lower()) # create schema if not exists - wait for schema to be created
        data.to_sql(table_name, engine, schema=schema_name, if_exists='replace', index=False)
        print("Data has been successfully stored in the database at a new table.")
            
    except Exception as e:
            print("An error occurred while storing data in the database:", e)
            return False
    return True

async def get_table_as_df(schema_name, table_name):
    
    metadata = get_metadata(schema=schema_name)

    # Check if the table exists
    if f'{schema_name}.{table_name}' not in metadata.tables:
        raise ValueError(f"Table {schema_name}.{table_name}' does not exist in the database")

    # Get the table from metadata
    table = metadata.tables[f'{schema_name}.{table_name}']

    # Query the database to get all rows from the table
    result = None
    
    with get_db_session() as session:
        result = session.query(table).all()

    # Convert the result to a DataFrame
    # df = pd.DataFrame(result)
    df = pd.DataFrame(result, columns=table.columns.keys())

    
    return df
