cd ~/environment/stream3_working_with_image/image-outpainting/

sam build
sam deploy --guided


Stack Name: image-outpainting
AWS Region: your current region (i.e. us-west-2, us-east-1)
Parameter S3BucketName: leave as default
Parameter ImagePrefix: leave as default
Parameter GeneratedImagePrefix: leave as default
Parameter BedrockModelId: leave as default
Confirm changes before deploy: N
Allow SAM CLI IAM role creation: leave as default
Disable rollback: leave as default
Save arguments to configuration file: leave as default
SAM configuration file: leave as default
SAM configuration environment: leave as default

cd ~/environment/stream3_working_with_image/image-outpainting/ui/

cd ~/environment/stream3_working_with_image/image-outpainting/ui/
python3.9 -m pip install -r requirements.txt

streamlit run app.py

# clean up resources
cd ~/environment/stream3_working_with_image/image-outpainting/

aws s3 rm s3://<image-bucket-name> --recursive

sam delete --stack-name image-outpainting --no-prompts 

