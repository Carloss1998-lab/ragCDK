import os
import boto3
import json
runtime= boto3.client('runtime.sagemaker') 
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", None)

 
MAX_NEW_TOKENS = 512
TOP_K = 50
TOP_P = 0.3
DO_SAMPLE = True 
REP_PEN = 1.03
TEMP = 0.1


def handler(event, context):
    body = json.loads(event['body'])
    prompt = body['inputs']
        
    payload = {
    "inputs": prompt,
    "parameters": {
        "do_sample":DO_SAMPLE,
        "top_p" : TOP_P,
        "temperature" :TEMP,
        "top_k":TOP_K,
        "max_new_tokens": MAX_NEW_TOKENS,
        "repetition_penalty":REP_PEN,
        "return_full_text": False
    }
    }

    payload = json.dumps(payload).encode('utf-8')
    
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, 
                                  ContentType= 'application/json', 
                                  Body=payload)
    
    model_predictions = json.loads(response['Body'].read())

    generated_text = model_predictions[0]['generated_text']
    
    message = {"prompt": prompt,'generated_text':generated_text}
    
    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json"
        }
    }
