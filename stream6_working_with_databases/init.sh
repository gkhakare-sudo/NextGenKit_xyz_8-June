cd ~/environment/stream6_working_with_databases
python3.9 -m pip install -r requirements.txt --upgrade

Go to CloudFormation Console 
Click on using-genai-for-private-files-workshop stack and click Outputs tab
Copy the value of MySQLEndpoint
Then, go to the AWS Secrets Manager Console 
Click on mysql_secrets secret
Under Secret value click Retrieve secret value
Then, click Edit
Click + Add row
For key type host for the value paste the value copied earlier
Click Save

python load_data.py

streamlit run app.py


Can you list the customers who have spent more than $500 in total?

