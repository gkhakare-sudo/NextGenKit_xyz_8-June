REGION=$(aws configure get region)
echo $REGION
AOSSENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchCollectionEndpoint`].OutputValue' \
  --output text)
echo $AOSSENDPOINT
ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`AmazonBedrockExecutionRoleARN`].OutputValue' \
  --output text)
echo $ROLE_ARN
OPENSEARCH_COLLECTION_ARN=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchCollectionArn`].OutputValue' \
  --output text)
echo $OPENSEARCH_COLLECTION_ARN
OPENSEARCH_S3_BUCKET_ARN=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchS3BucketARN`].OutputValue' \
  --output text)
echo $OPENSEARCH_S3_BUCKET_ARN
OpenSearch_BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name using-genai-for-private-files-workshop --query "Stacks[0].Outputs[?OutputKey=='OpenSearchS3Bucket'].OutputValue" --output text)
echo $OpenSearch_BUCKET_NAME