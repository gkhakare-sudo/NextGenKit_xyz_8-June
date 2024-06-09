cd ~/environment/stream2_working_with_private_documents/bedrock_and_kendra
python3.9 -m pip install -r requirements.txt --upgrade
KENDRA_INDEX_ID=$(aws cloudformation describe-stacks --stack-name using-genai-for-private-files-workshop --query "Stacks[0].Outputs[?OutputKey=='WorkshopKendraIndexId'].OutputValue" --output text)

IAM_ROLE_ARN=$(aws cloudformation describe-stacks --stack-name using-genai-for-private-files-workshop --query "Stacks[0].Outputs[?OutputKey=='WorkshopRoleArn'].OutputValue" --output text)

aws kendra create-data-source --name "WebCrawlerSourceLambda" --type "WEBCRAWLER" --configuration '{"WebCrawlerConfiguration": {"Urls": {"SiteMapsConfiguration": {"SiteMaps": ["https://docs.aws.amazon.com/lambda/latest/dg/sitemap.xml"]}}, "UrlInclusionPatterns": [".*https://docs.aws.amazon.com/lambda/.*"]}}' --index-id "${KENDRA_INDEX_ID}" --role-arn "${IAM_ROLE_ARN}"

aws kendra start-data-source-sync-job --index-id "${KENDRA_INDEX_ID}" --id '<Id>'


streamlit run app.py