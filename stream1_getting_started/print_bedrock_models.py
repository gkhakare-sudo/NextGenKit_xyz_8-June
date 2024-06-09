import boto3
import json
import os

client = boto3.client('bedrock')

model_data = client.list_foundation_models()
print(json.dumps(model_data, sort_keys=True, indent=4))
model_ids = [model['modelId'] for model in model_data['modelSummaries']]
#print("Total models:")
#print("")
#print('\n'.join(model_ids))

