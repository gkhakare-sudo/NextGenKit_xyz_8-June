import boto3
import json
import os
import argparse

client= boto3.client('bedrock-runtime')

parser= argparse.ArgumentParser()

parser.add_argument("--prompt",type=str, required=True, help="Promopt here")
parser.add_argument("--modelid", type=str, required=True, help="Model Id")

args= parser.parse_args()

modelId=args.modelid
accept="application/json"
contentType="application/json"



prompt_data = args.prompt;

print(prompt_data+" "+modelId)

titan_input= json.dumps({
    "inputText": prompt_data,
    "textGenerationConfig": {
        "maxTokenCount": 512,
        "stopSequences": [],
        "temperature": 0.1,
        "topP": 0.9,
        
    }
})

claude_input = json.dumps({
    "prompt": f'Human: {args.prompt}\nAssistant:', 
    "max_tokens_to_sample": 500,
    "temperature": 0.5,
    "top_k": 250,
    "top_p": 1,
    "stop_sequences": [
    ]
})

if modelId == "amazon.titan-text-express-v1":
    response= client.invoke_model(body=titan_input, modelId=modelId, accept=accept, contentType=contentType)
    response_body= json.loads(response.get("body").read())
    print(response_body.get("results")[0].get("outputText"))

if modelId == "anthropic.claude-v2":
    response = client.invoke_model(body=claude_input, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    print(response_body['completion'])
    
