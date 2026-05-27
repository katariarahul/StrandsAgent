import boto3
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure your Boto3 version is >= 1.43.11

session = boto3.Session()

client = boto3.client("bedrock-agentcore", region_name="ap-south-1")
# 2. Define target metadata
# Replace with your target runtime ARN or Agent ID
agent_arn_value: str = os.getenv("AGENT_ARN")
#print("....",agent_arn_value)

try:
    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn_value,
        runtimeSessionId="my-first-test-session-for-testing-00001",
        payload=json.dumps({
            "prompt": "What time is it?"
        })
    )
    #print(response)
except Exception as e: 
    print(e)

# OR - more better style

payload_data = {
    "prompt": "Analyze our Q3 cloud expenditures and spot anomalies."
}

# Invoke the agent runtime
# The response payload returns as a stream
response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn_value,
    runtimeSessionId=str(uuid.uuid4()), # Explicit session isolation
    contentType="application/json",
    accept="application/json",
    payload=json.dumps(payload_data).encode('utf-8'),
    qualifier="DEFAULT" # Points to a specific version or endpoint
)

streaming_body = response.get("response")
if streaming_body:
    # Read and decode the full body payload block 
    raw_payload_str = streaming_body.read().decode('utf-8')
    
    print(raw_payload_str)