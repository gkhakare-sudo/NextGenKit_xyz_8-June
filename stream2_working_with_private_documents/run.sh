cd ~/environment/stream2_working_with_private_documents/bedrock_and_opensearch/
python download_dataset.py
aws s3 cp ./docs s3://${OpenSearch_BUCKET_NAME}/ --recursive
aws bedrock-agent start-ingestion-job --knowledge-base-id $KNOWLEDGE_BASE_ID --data-source-id $DATA_SOURCE_ID
streamlit run app.py

