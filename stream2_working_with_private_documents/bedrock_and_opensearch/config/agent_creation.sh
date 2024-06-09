aws bedrock-agent create-data-source \
  --knowledge-base-id $KNOWLEDGE_BASE_ID \
  --name workshop-kb-data-source \
  --data-source-configuration "type=S3,s3Configuration={bucketArn=${OPENSEARCH_S3_BUCKET_ARN}}"
DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources --knowledge-base-id $KNOWLEDGE_BASE_ID | jq -r '.dataSourceSummaries[0].dataSourceId')
echo $DATA_SOURCE_ID