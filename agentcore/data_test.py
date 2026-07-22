import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')
payload = json.dumps({"prompt": "Data, who is Q and why is he like that? No spoilers please!"})

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:571761132122:runtime/data_agent_agentcore-f9HrFl9WcX',
    runtimeSessionId='adjfoijewaoifjoiewajoifjawejfoiwajfjiewa', # Must be 33+ char. Every new SessionId will create a new MicroVM
    payload=payload,
    qualifier="DEFAULT" # This is Optional. When the field is not provided, Runtime will use DEFAULT endpoint
)
response_body = response['response'].read()
response_data = json.loads(response_body)
print("Agent Response:", response_data)