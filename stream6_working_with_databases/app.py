import streamlit as st
import pandas as pd
import mysql.connector
import boto3
import json
import re

st.set_page_config(layout="wide")

# Custom CSS to reduce space above the title
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
</style>
""", unsafe_allow_html=True)

def get_secret(secret_name):
    # Initialize a session using Amazon Secrets Manager
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    # Get the secret value
    get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# Function to connect to the database
def connect_to_db():
    # Fetch the secret values
    secret_name = "mysql_secrets"
    secret_values = get_secret(secret_name)

    try:
        connection = mysql.connector.connect(
            host=secret_values['host'],
            user=secret_values['username'],
            password=secret_values['password'],
            port=secret_values['port'],
            database=secret_values['dbname']
        )
        if connection.is_connected():
            return connection
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def interact_with_llm(query):
    client = boto3.client('bedrock-runtime')
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    hardcoded_context = """
    sales database has three tables:
    1. products with columns:
    ProductID INT PRIMARY KEY,
    ProductName VARCHAR(255) NOT NULL,
    Description TEXT,
    Price DECIMAL(10, 2) NOT NULL,
    StockQuantity INT NOT NULL,
    CategoryID INT

    2. customers with columns:
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Address TEXT,
    Phone VARCHAR(15)

    3. orders with columns:
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    ProductID INT,
    Quantity INT NOT NULL,
    OrderDate DATE NOT NULL,
    TotalPrice DECIMAL(10, 2) NOT NULL

    generate a sql command between <begin sql> and </end sql>
    """

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

    response = client.invoke_model(body=claude_input, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    return response_body['completion']
    
def main():
    
    st.title("MySQL Database Interaction with LLM")

    # Connect to the database
    connection = connect_to_db()

    if connection:
        st.success("Connection to the database was successful!")
        
        # Create three columns for products, customers, and orders tables
        col1, col2, col3 = st.columns(3)

        # Display the 'products' table
        try:
            query = "SELECT * FROM products;"
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            columns = cursor.column_names
            df_products = pd.DataFrame(result, columns=columns)
            col1.markdown("<div style='text-align: center; font-weight: bold;'>Products Table</div>", unsafe_allow_html=True)
            col1.dataframe(df_products)
        except Exception as e:
            st.error(f"Error fetching products data: {e}")

        # Display the 'customers' table
        try:
            query = "SELECT * FROM customers;"
            cursor.execute(query)
            result = cursor.fetchall()
            columns = cursor.column_names
            df_customers = pd.DataFrame(result, columns=columns)
            col2.markdown("<div style='text-align: center; font-weight: bold;'>Customers Table</div>", unsafe_allow_html=True)
            col2.dataframe(df_customers)
        except Exception as e:
            st.error(f"Error fetching customers data: {e}")

        # Display the 'orders' table
        try:
            query = "SELECT * FROM orders;"
            cursor.execute(query)
            result = cursor.fetchall()
            columns = cursor.column_names
            df_orders = pd.DataFrame(result, columns=columns)
            col3.markdown("<div style='text-align: center; font-weight: bold;'>Orders Table</div>", unsafe_allow_html=True)
            col3.dataframe(df_orders)
        except Exception as e:
            st.error(f"Error fetching orders data: {e}")

        # LLM Interaction
        user_query = st.text_input("Enter your question:")

        if user_query:
            llm_response = interact_with_llm(user_query)
            # Convert multiline llm_response to single line
            llm_response = llm_response.replace('\n', ' ').replace('\r', ' ')
            st.write(f"LLM Response: {llm_response}")

            # Extract SQL command from LLM response
            sql_command_match = re.search(r'<begin sql>(.*?)<\s?/end sql>', llm_response, re.DOTALL | re.IGNORECASE)
            if sql_command_match:
                sql_command = sql_command_match.group(1).strip()
                try:
                    cursor.execute(sql_command)
                    result = cursor.fetchall()
                    columns = cursor.column_names
                    df = pd.DataFrame(result, columns=columns)
                    st.write(df)
                except Exception as e:
                    st.error(f"Error executing SQL command: {e}")
            else:
                st.warning("No SQL command found in LLM response.")

        connection.close()

if __name__ == "__main__":
    main()


