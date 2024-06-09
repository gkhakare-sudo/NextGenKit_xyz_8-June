KNOWLEDGE_BASE_ID=$(aws bedrock-agent create-knowledge-base \
  --name workshop-aoss-knowledge-base \
  --role-arn $ROLE_ARN \
  --knowledge-base-configuration 'type=VECTOR,vectorKnowledgeBaseConfiguration={embeddingModelArn="arn:aws:bedrock:'${REGION}'::foundation-model/amazon.titan-embed-text-v1"}' \
  --storage-configuration "type=OPENSEARCH_SERVERLESS,opensearchServerlessConfiguration={collectionArn='${OPENSEARCH_COLLECTION_ARN}',vectorIndexName='workshop_index',fieldMapping={vectorField='documentid',textField='workshop-data',metadataField='workshop-metadata'}}" \
  | jq -r '.knowledgeBase.knowledgeBaseId')
echo $KNOWLEDGE_BASE_ID
