import boto3
import json
import os
import argparse

client = boto3.client('bedrock-runtime')

parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True, help="Prompt for text generation")
parser.add_argument("--modelid", type=str, required=True, help="Model ID for generation")
args = parser.parse_args()

modelId = args.modelid  
accept = 'application/json'
contentType = 'application/json'

# Read the prompt from a text file
with open(args.file, "r") as file:
    prompt_data = file.read().strip()

# Format the prompt to start with "Human:" and end with "Assistant:"
formatted_prompt = f'Human: Please provide a summary of the following text in one small paragraph. {prompt_data} \n\nAssistant:'

claude_input = json.dumps({
    "prompt": formatted_prompt, 
    "max_tokens_to_sample": 500,
    "temperature": 0.5,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": []
})

response = client.invoke_model(body=claude_input, modelId=modelId, accept=accept, contentType=contentType)
response_body = json.loads(response.get('body').read())
print(response_body['completion'])
