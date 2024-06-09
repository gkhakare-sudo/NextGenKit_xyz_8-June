import streamlit as st
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import __
import boto3
import json
import os

g = None
connection_string = os.environ.get('NEPTUNE_CONNECTION_STRING')

# Function to connect to the graph
def connect_to_graph():
    global g
    graph = Graph()
    remoteConn = DriverRemoteConnection(connection_string, 'g')
    g = graph.traversal().withRemote(remoteConn)
    print('Connection created.')
    return g


# Function to get query code from the language model
def get_query_code_from_model(question):
    hardcoded_context = """
    The Amazon Neptune graph database contains vertices representing various entities in the fashion retail domain:
    
    - product vertices with properties:
      - name (e.g., shirt, jeans, shoes, etc.)
      - color (e.g., blue, black, white, etc.)
      - brand (e.g., Fashionista, TrendyDenim, WalkEasy, etc.)
      - size (e.g., M, L, OneSize, etc.)
      - price (numeric value)
    
    - brand vertices with properties:
      - name (e.g., Fashionista, TrendyDenim, WalkEasy, etc.)
      - origin (e.g., Italy, USA, Spain, etc.)
    
    - category vertices with properties:
      - name (e.g., Clothing, Footwear, Accessories, Jewelry)
    
    Relationships include:
    - product vertices belonging to a specific brand (belongs_to_brand)
    - product vertices belonging to a specific category (belongs_to_category)
    
    Generate a gremlin query between the tags <begin code> and </end code>
    """

    prompt_data = f"""\n\nHuman: In case you don't have the information in context provided, please respond with 'I don't know'.
    <context>
    {hardcoded_context}
    </context>
    <question>
    {question}
    </question>
    \n\nAssistant:"""
    
    claude_input = json.dumps({
        "prompt": prompt_data, 
        "max_tokens_to_sample": 500,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": []
    })

    client = boto3.client('bedrock-runtime')
    response = client.invoke_model(body=claude_input, modelId="anthropic.claude-v2", accept="application/json", contentType="application/json")
    response_body = json.loads(response.get('body').read())
    completion = response_body['completion']
    
    print(completion)
    # Normalize the completion string
    normalized_completion = completion.strip()
    
    # Check for the presence of <begin code> and <end code> tags
    if '<begin code>' in normalized_completion and '</end code>' in normalized_completion:
        start_idx = normalized_completion.find('<begin code>') + len('<begin code>')
        end_idx = normalized_completion.rfind('</end code>')
    # Else, check for the presence of <code> and </code> tags
    elif '<code>' in normalized_completion and '</code>' in normalized_completion:
        start_idx = normalized_completion.find('<code>') + len('<code>')
        end_idx = normalized_completion.rfind('</code>')
    else:
        # If neither set of tags is found, return an error or default message
        return "Error extracting query from model output."
    
    code = normalized_completion[start_idx:end_idx].strip()
    print(code)
    return code

# Function to execute the query on the database
def execute_query(query_code, g):
    query_code = query_code.replace(".in(", ".in_(")
    final_query = f"{query_code}.toList()"
    print("Final Query to DB:", final_query)
    
    try:
        local_vars = {}
        global_vars = {"g": g}
        exec(f"result = {final_query}", global_vars, local_vars)
        print("Query executed successfully.")
        result = local_vars["result"]
        
        print("Query Result:", result)
        return result
    except Exception as e:
        print("Error encountered:", str(e))
        return f"Error executing the query: {str(e)}"


# Streamlit UI
st.title("Amazon Neptune query with natural language")

# Text field for users to ask questions
question = st.text_input("Ask a question:")

if question:
    # Get the query code from the language model
    query_code = get_query_code_from_model(question)

    # Print the intermediate model output
    st.write("Model Output:", query_code)

    if "I don't know" in query_code:
        st.write("I don't have enough information to answer that question.")
    else:
        if g is None:
            g = connect_to_graph()
        # Execute the query on the database
        result = execute_query(query_code, g)
        if isinstance(result, list):
            for item in result:
                st.write(item)
        else:
            st.write("Result:", result)
