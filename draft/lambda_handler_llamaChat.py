import os
import boto3
import json
runtime= boto3.client('runtime.sagemaker') 
ENDPOINT_NAME = os.environ.get("SAGEMAKER_ENDPOINT_NAME", None)

MAX_NEW_TOKENS = 120
TOP_P = 0.3
TEMP = 0.2

def build_llama2_prompt(messages):
    startPrompt = "<s>[INST] "
    endPrompt = " [/INST]"
    conversation = []
    for index, message in enumerate(messages):
        if message["role"] == "system" and index == 0:
            conversation.append(f"<<SYS>>\n{message['content']}\n<</SYS>>\n\n")
        elif message["role"] == "user":
            conversation.append(message["content"].strip())
        else:
            conversation.append(f" [/INST] {message['content'].strip()}</s><s>[INST] ")

    return startPrompt + "".join(conversation) + endPrompt

def format_event_to_messages(event):
    messages = []
    for role, content in event.items():
        messages.append({"role": role, "content": content})
    return messages

def handler(event, context):
    body = json.loads(event['body'])
  
    messages = format_event_to_messages(body)

    prompt = build_llama2_prompt(messages)
    payload = {
    "inputs": prompt,
    "parameters": {
        "top_p" : TOP_P,
        "temperature" :TEMP,
        "max_new_tokens": MAX_NEW_TOKENS,
    }
    }

    payload = json.dumps(payload).encode('utf-8')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, 
                                  ContentType= 'application/json', 
                                  Body=payload,
                                  CustomAttributes="accept_eula=true")

    model_predictions = json.loads(response['Body'].read())
    message =model_predictions[0]["generated_text"][len(prompt):]

    return {
        "statusCode": 200,
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json"
        }
    }
