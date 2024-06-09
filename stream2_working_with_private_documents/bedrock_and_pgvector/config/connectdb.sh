psql -h $Aurora_Cluster_Writer_Endpoint -d postgres -U workshopUser -p 3306
CREATE EXTENSION IF NOT EXISTS vector;
SELECT extversion FROM pg_extension WHERE extname='vector';
CREATE SCHEMA bedrock_integration;
CREATE ROLE bedrock_user WITH PASSWORD 'workshoppassword@1' LOGIN;
GRANT ALL ON SCHEMA bedrock_integration to bedrock_user;
\q 
psql -h $Aurora_Cluster_Writer_Endpoint -d postgres -U bedrock_user -p 3306
CREATE TABLE bedrock_integration.bedrock_kb (id uuid PRIMARY KEY, embedding vector(1536), chunks text, metadata json);
CREATE INDEX on bedrock_integration.bedrock_kb USING hnsw (embedding vector_cosine_ops);
\q

Go to the AWS Secrets Manager Console 
Click the button Store a new secret
Select secret type as Credentials for Amazon RDS database
Provide the username bedrock_user and password workshoppassword@1
Under Database, select workshopdbcluster
Click Next and provide secret name postgres_kb_secret
Click Next > Next > Store

SECRET_ARN=$(aws secretsmanager list-secrets --query 'SecretList[?Name==`postgres_kb_secret`].ARN' --output text)
echo $SECRET_ARN


Knowledge_Base_Id=$(aws bedrock-agent create-knowledge-base \
  --name workshop-aurora-knowledge-base \
  --role-arn $ROLE_ARN \
  --knowledge-base-configuration 'type=VECTOR,vectorKnowledgeBaseConfiguration={embeddingModelArn="arn:aws:bedrock:'"$REGION"'::foundation-model/amazon.titan-embed-text-v1"}' \
  --storage-configuration 'type=RDS,rdsConfiguration={resourceArn='"$Aurora_Cluster_Arn"',credentialsSecretArn='"$SECRET_ARN"',databaseName=postgres,tableName=bedrock_integration.bedrock_kb,fieldMapping={primaryKeyField=id,vectorField=embedding,textField=chunks,metadataField=metadata}}'\
  | jq -r '.knowledgeBase.knowledgeBaseId')
  echo $Knowledge_Base_Id


Go to the AWS Secrets Manager Console 
Click on postgres_vectors_secrets secret
Under Secret value click Retrieve secret value
Then, click Edit
Click + Add row
For key type KNOWLEDGE_BASE_ID and for the value paste the value of KNOWLEDGE_BASE_ID printed in the terminal above
Click Save


Data_Source_Id=$(aws bedrock-agent create-data-source \
  --knowledge-base-id $Knowledge_Base_Id \
  --name workshop-aurora-kb-data-source \
  --data-source-configuration "type=S3,s3Configuration={bucketArn='"$Postgres_Bucket_Arn"'}" \
  --vector-ingestion-configuration "chunkingConfiguration={chunkingStrategy=NONE}" \
  | jq -r '.dataSource.dataSourceId')
echo $Data_Source_Id



