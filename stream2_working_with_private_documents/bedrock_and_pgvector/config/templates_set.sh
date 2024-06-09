ROLE_ARN=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`AmazonBedrockExecutionRoleARN`].OutputValue' \
  --output text)
echo $ROLE_ARN
REGION=$(aws configure get region)
echo $REGION
Aurora_Cluster_Writer_Endpoint=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`AuroraDBWriterEndpoint`].OutputValue' \
  --output text)
echo $Aurora_Cluster_Writer_Endpoint
Aurora_Cluster_Arn=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`AuroraDBClusterARN`].OutputValue' \
  --output text)
echo $Aurora_Cluster_Arn
Postgres_Bucket_Name=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`WorkshopPostgreS3BucketName`].OutputValue' \
  --output text)
echo $Postgres_Bucket_Name
Postgres_Bucket_Arn=$(aws cloudformation describe-stacks \
  --stack-name 'using-genai-for-private-files-workshop' \
  --query 'Stacks[0].Outputs[?OutputKey==`WorkshopPostgreS3BucketARN`].OutputValue' \
  --output text)
echo $Postgres_Bucket_Arn
DB_Password=$(aws secretsmanager get-secret-value --secret-id postgres_vectors_secrets --query SecretString --output text | jq -r .password)
echo "DB_Password: $DB_Password"
