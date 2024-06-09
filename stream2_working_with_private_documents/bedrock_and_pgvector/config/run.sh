cd ~/environment/stream2_working_with_private_documents/bedrock_and_pgvector/

python download_dataset.py

aws s3 cp ./docs s3://${Postgres_Bucket_Name}/ --recursive


aws bedrock-agent start-ingestion-job --knowledge-base-id $Knowledge_Base_Id --data-source-id $Data_Source_Id

streamlit run app.py
