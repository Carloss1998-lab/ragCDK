import os
import boto3
import json

runtime= boto3.client('runtime.sagemaker') 
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", None)
 

def handler(event, context):
    body = json.loads(event['body'])
    payload = {
    "text_prompts":[{
        "text": body["prompt"], 
        "weight":"1.0"}],
    "samples":1}
    request = json.dumps(payload).encode('utf-8')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, 
                                      Body=request, 
                                      ContentType='application/json')    
    response_body = json.loads(response['Body'].read().decode())
    return {
               'headers': { "Content-Type": "*/*" },
               'statusCode': 200,
               'body': response_body["artifacts"][0]["base64"],
               'isBase64Encoded': True
           }