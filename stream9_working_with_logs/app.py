import streamlit as st
import boto3
import time
import json
import re
import pandas as pd
import os

# Initialize the boto3 clients
bedrock_client = boto3.client('bedrock-runtime')
athena_client = boto3.client('athena')

DATABASE_NAME = 'logs_glue_db'
WORKGROUP_NAME = 'primary'
bucket_name = os.environ['bucket_name']
S3_OUTPUT_LOCATION = f's3://{bucket_name}/athena_output/'

# Bedrock model details
modelId = 'anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

hardcoded_context = """
    In the AWS ecosystem, we use Amazon Athena to query datasets on Amazon S3. The structure of our data is defined in AWS Glue Data Catalog. For this exercise, consider the Glue Data Catalog database named 'logs_glue_db' and a table named 'logs_glue_table' within it. This table in turn points to data stored as Parquet files on S3 bucket.

    'logs_glue_db.logs_glue_table' schema is as follows:
    
    1. timestamp: Type is STRING. Represents the time a log was created.
    2. log_level: Type is STRING. Indicates the severity level of the log (e.g., INFO, WARN, ERROR).
    3. message: Type is STRING. Contains the detailed log message.
    4. host: Type is STRING. Indicates the source or the host machine where the log originated.
    5. thread: Type is INT. Represents the ID of the thread that produced the log.
    6. request_id: Type is STRING. A unique identifier for each request causing the log.

    Given this context, help in generating Athena SQL queries to fetch data based on user requirements. generate a sql command between <begin sql> and </end sql>.
"""

def get_sql_from_prompt(query):
    try:
        # Convert user prompt to SQL using AWS Bedrock
        prompt_data = f"""Human: In case you don't have the information in context provided, please respond with 'I don't know'.
        <context>
        {hardcoded_context}
        </context>
        <question>
        {query}
        </question>
        Assistant:"""
    
        claude_input = json.dumps({
            "prompt": prompt_data,
            "max_tokens_to_sample": 500,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
            "stop_sequences": []
        })
    
        response = bedrock_client.invoke_model(body=claude_input, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        assistant_response = response_body['completion'].strip()
        
        # Extracting SQL between the tags
        sql_match = re.search(r"<begin sql>(.*?)</end sql>", assistant_response, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        else:
            return "I don't know"
    except Exception as e:
        st.error(f"Error in generating SQL: {e}")
        return "I don't know"

def run_athena_query(sql):
    # Start the Athena query
    response = athena_client.start_query_execution(
        QueryString=sql,
        QueryExecutionContext={
            'Database': DATABASE_NAME
        },
        ResultConfiguration={
            'OutputLocation': S3_OUTPUT_LOCATION
        },
        WorkGroup=WORKGROUP_NAME
    )
    return response['QueryExecutionId']

def get_query_results(query_id):
    while True:
        response = athena_client.get_query_execution(
            QueryExecutionId=query_id
        )
        state = response['QueryExecution']['Status']['State']
        if state == 'SUCCEEDED':
            return athena_client.get_query_results(QueryExecutionId=query_id)
        elif state == 'FAILED' or state == 'CANCELLED':
            raise Exception('Athena query failed or was cancelled')
        time.sleep(1)


def json_to_table(data):
    # Extract column headers
    columns = [item["VarCharValue"] for item in data[0]]

    # Extract rows
    rows = []
    for entry in data[1:]:
        row = [item["VarCharValue"] for item in entry]
        rows.append(row)

    # Convert rows to pandas DataFrame
    df = pd.DataFrame(rows, columns=columns)
    return df

st.title('Athena Query via Bedrock')

# Take user input
user_input = st.text_input("Enter your query in plain English:")

if st.button('Run Query'):
    try:
        # Convert input to SQL
        sql = get_sql_from_prompt(user_input)
        
        # Display the SQL output
        st.write("Generated Athena query:")
        st.text(sql)
        
        # If Bedrock couldn't generate a query
        if sql == "I don't know":
            st.warning("Couldn't generate a query based on the provided input.")
            st.stop()   # Use st.stop() instead of return
        
        # Execute SQL on Athena
        query_id = run_athena_query(sql)
        
        # Fetch results
        results = get_query_results(query_id)
        
        # Extract and transform data from results
        rows_data = results['ResultSet']['Rows']
        columns = [data['VarCharValue'] for data in rows_data[0]['Data']]
        table_data = []
        for row in rows_data[1:]:
            table_data.append({columns[i]: entry['VarCharValue'] for i, entry in enumerate(row['Data'])})

        # Display the table
        st.table(table_data)
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
